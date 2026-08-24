import time
import asyncio
import threading
import RPi.GPIO as GPIO
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
    ModbusServerContext
)

# Global thread lock to prevent datastore read/write collisions
data_lock = threading.Lock()

# Initialize GPIO in BCM numbering mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# HARDWARE GPIO PIN MAPPINGS FOR TB6612FNG MOTOR DRIVER
MOTORS = {
    1: {
        'pwm_pin': 17,  # PWMA (Motor 1 Speed)
        'in1_pin': 18,  # AIN1 (Motor 1 Direction Bit 1)
        'in2_pin': 27,  # AIN2 (Motor 1 Direction Bit 2)
        'pwm_obj': None,
        'last_rpm': None # Latch state to prevent unnecessary PWM updates
    },
    2: {
        'pwm_pin': 23,  # PWMB (Motor 2 Speed)
        'in1_pin': 24,  # BIN1 (Motor 2 Direction Bit 1)
        'in2_pin': 25,  # BIN2 (Motor 2 Direction Bit 2)
        'pwm_obj': None,
        'last_rpm': None
    }
}

STBY_PIN = 22 # Driver Standby Pin (High = Driver Enabled)

# Setup GPIO pins and PWM channels
GPIO.setup(STBY_PIN, GPIO.OUT)
GPIO.output(STBY_PIN, 1) # Keep TB6612FNG active

for m in MOTORS.values():
    GPIO.setup(m['pwm_pin'], GPIO.OUT)
    GPIO.setup(m['in1_pin'], GPIO.OUT)
    GPIO.setup(m['in2_pin'], GPIO.OUT)
    
    # Initialize 1kHz PWM signal for DC motor speed control
    m['pwm_obj'] = GPIO.PWM(m['pwm_pin'], 1000)
    m['pwm_obj'].start(0)

# SMOOTH MOTOR EXECUTION THREAD
def run_axis(context, motor_id, reg_addr):
    """Dedicated execution thread with smooth PWM state latching."""
    m = MOTORS[motor_id]
    
    while True:
        try:
            # Safely fetch values using the thread lock
            with data_lock:
                slave_ctx = context[0]
                raw_val = slave_ctx.getValues(3, reg_addr, count=1)[0]
            
            signed_rpm = raw_val if raw_val < 32768 else raw_val - 65536
            
            # Only update GPIO outputs if the speed/direction command actually changed
            if signed_rpm != m['last_rpm']:
                m['last_rpm'] = signed_rpm
                
                if signed_rpm == 0:
                    # Motor Stopped / Brakes applied
                    m['pwm_obj'].ChangeDutyCycle(0)
                    GPIO.output(m['in1_pin'], 0)
                    GPIO.output(m['in2_pin'], 0)
                else:
                    # Direction Logic
                    if signed_rpm > 0:
                        # Forward
                        GPIO.output(m['in1_pin'], 1)
                        GPIO.output(m['in2_pin'], 0)
                    else:
                        # Reverse
                        GPIO.output(m['in1_pin'], 0)
                        GPIO.output(m['in2_pin'], 1)
                    
                    # Scale RPM command (0 to 100) to max 50% PWM Duty Cycle
                    duty_cycle = min(abs(signed_rpm) * 0.5, 50)
                    m['pwm_obj'].ChangeDutyCycle(duty_cycle)
        except Exception:
            # On transient read error, HOLD the last valid motor speed instead of stopping
            pass
            
        time.sleep(0.02) # Faster 20ms update cycle for smooth response

# LIVE DIAGNOSTIC MONITORING THREAD
def monitor_loop(context):
    """Live diagnostic thread to monitor OpenPLC Modbus TCP commands on console."""
    while True:
        try:
            with data_lock:
                slave_ctx = context[0]
                regs = slave_ctx.getValues(3, 200, count=2)
                
            s1 = regs[0] if regs[0] < 32768 else regs[0] - 65536
            s2 = regs[1] if regs[1] < 32768 else regs[1] - 65536
            
            dir1 = "FWD" if s1 > 0 else ("REV" if s1 < 0 else "STP")
            dir2 = "FWD" if s2 > 0 else ("REV" if s2 < 0 else "STP")
            
            print(f"[SCADA Live Wire] Reg 200 (M1): {s1:4d} RPM [{dir1}] | Reg 201 (M2): {s2:4d} RPM [{dir2}]")
        except Exception:
            pass
        time.sleep(1.0)

# MAIN ENTRY POINT
if __name__ == "__main__":
    print("--- Raspberry Pi N20 DC Motor RTU Online ---")
    print("--- Listening on IP: 192.168.2.220 | Port: 502 | Slave ID: 1 ---")
    
    # Allocate Modbus memory block starting at Holding Register 200
    store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(200, [0] * 10))
    context = ModbusServerContext(slaves=store, single=True)
    
    # Launch independent execution threads for each motor axis
    t1 = threading.Thread(target=run_axis, args=(context, 1, 200), daemon=True)
    t2 = threading.Thread(target=run_axis, args=(context, 2, 201), daemon=True)
    t_mon = threading.Thread(target=monitor_loop, args=(context,), daemon=True)
    
    t1.start()
    t2.start()
    t_mon.start()
    
    try:
        asyncio.run(StartAsyncTcpServer(context=context, address=("192.168.2.220", 502)))
    except KeyboardInterrupt:
        print("\n[Shutdown] Operator triggered KeyboardInterrupt (Ctrl+C)")
    finally:
        print("[Shutdown] Stopping PWM and cleaning up GPIO pins...")
        for m in MOTORS.values():
            m['pwm_obj'].stop()
        GPIO.output(STBY_PIN, 0)
        GPIO.cleanup()
        print("[Shutdown] System offline.")