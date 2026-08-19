PROGRAM scada
  VAR
    Button_Edge : R_TRIG;
    Motor1_Toggle : BOOL;
  END_VAR
  VAR
    Safety_Latch AT %QX0.4 : BOOL;
    HMI_E_Stop AT %QX0.1 : BOOL;
    HMI_Reset AT %QX0.2 : BOOL;
    Raw_Temp AT %IW0 : INT;
    Push_Button AT %IX0.0 : BOOL;
    Motor1_Speed AT %QW0 : INT;
    Motor2_Speed AT %QW1 : INT;
    Motor1_Status AT %QX0.5 : BOOL;
    Motor2_Status AT %QX0.6 : BOOL;
    HMI_Temp AT %MW0 : INT;
    HMI_Button AT %QX0.7 : BOOL;
    HMI_Motor1_Cmd AT %MW1 : INT;
    HMI_Motor2_Cmd AT %MW2 : INT;
    HMI_Motor1_Enable AT %QX1.0 : BOOL;
    HMI_Motor2_Enable AT %QX1.1 : BOOL;
    HMI_Motor1_Dir AT %QX1.2 : BOOL;
    HMI_Motor2_Dir AT %QX1.3 : BOOL;
  END_VAR

  (* 0. SAFETY LATCH LOGIC (Converted from Ladder Rung)                        *)
  Safety_Latch := (HMI_Reset OR Safety_Latch) AND NOT(HMI_E_Stop);

  (* 1. MIRROR ANALOG SENSORS & CALCULATE PREVIEW SPEED                        *)
  HMI_Temp := Raw_Temp;

  (* Always calculate intended speed from temperature so the operator          *)
  (* can preview what Motor 2 would run at on the dashboard gauge              *)
  IF Raw_Temp <= 3000 THEN
      HMI_Motor2_Cmd := 20;  (* Green Sector (<= 30�C): Cruise floor at 20 RPM *)
  ELSIF Raw_Temp >= 4000 THEN
      HMI_Motor2_Cmd := 100; (* Red Sector (>= 40�C): Max speed at 100 RPM *)
  ELSE
      (* Yellow Sector (30�C to 40�C): Linear proportional ramp from 20 to 100 RPM *)
      HMI_Motor2_Cmd := 20 + (((Raw_Temp - 3000) * 80) / 1000);
  END_IF;

  (* 2. FIELD BUTTON TOGGLE LOGIC (Edge Detection + Flip-Flop)                 *)
  Button_Edge(CLK := Push_Button);

  IF Button_Edge.Q THEN
      Motor1_Toggle := NOT(Motor1_Toggle);
  END_IF;

  (* Mirror latched state to Node-RED so your dashboard badge stays lit *)
  HMI_Button := Motor1_Toggle;

  (* 3. TIER 1: MASTER SAFETY INTERLOCK                                        *)
  IF NOT(Safety_Latch) THEN
      (* EMERGENCY STOP ACTIVE: Instantly drop both speeds to 0 and reset field toggle *)
      Motor1_Speed := 0;
      Motor2_Speed := 0;
      Motor1_Toggle := FALSE;
  ELSE
      (* SYSTEM SAFE: Evaluate individual motor control gates *)

      (* MOTOR 1: Manual HMI Channel (Direct Slider Follow)                    *)
      (* If EITHER HMI Enable is ON or Field Button is Toggled ON, follow slider *)
      IF (HMI_Motor1_Enable OR Motor1_Toggle) THEN
          IF HMI_Motor1_Dir THEN
              Motor1_Speed := ABS(HMI_Motor1_Cmd) * -1; (* Reverse *)
          ELSE
              Motor1_Speed := ABS(HMI_Motor1_Cmd);       (* Forward *)
          END_IF;
      ELSE
          Motor1_Speed := 0;
      END_IF;

      (* MOTOR 2: Automated Thermal Channel                                    *)
      (* If HMI Enable toggle is ON, drive the physical motor with preview RPM *)
      IF NOT(HMI_Motor2_Enable) THEN
          Motor2_Speed := 0;
      ELSE
          IF HMI_Motor2_Dir THEN
              Motor2_Speed := HMI_Motor2_Cmd * -1; (* Reverse *)
          ELSE
              Motor2_Speed := HMI_Motor2_Cmd;       (* Forward *)
          END_IF;
      END_IF;

  END_IF;

  (* 4. UPDATE MOTOR STATUS BADGES FOR NODE-RED LEDS                           *)
  Motor1_Status := (Motor1_Speed <> 0);
  Motor2_Status := (Motor2_Speed <> 0);
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 1);
    PROGRAM instance1 WITH task0 : scada;
  END_RESOURCE
END_CONFIGURATION
