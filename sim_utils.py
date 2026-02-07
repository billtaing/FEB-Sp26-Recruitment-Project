import numpy as np 
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

# constants:
pi = 3.14
g = 9.81 # m/s^2 accel due to gravity
rho = 1.225 # kg/m^3, air density

def simulate(mesh_size, params, track, mtc):
    # Step 1: Mesh the track
    sections = [list(track.keys())[0]] + [section for section, length in track.items() for _ in range(int(np.ceil(length/mesh_size)))]
    x = np.array([0])
    for length in track.values():
        start_of_segment = x[-1]
        x = np.append(x, np.arange(start_of_segment+mesh_size, start_of_segment+length+1, mesh_size))
        if x[-1] < start_of_segment+length:
            x = np.append(x, start_of_segment+length)
    dx = np.append(np.array([0]), x[1:] - x[:-1])
    r = [0 if section == 'straight' else params['t1 radius'] for section in sections]
    data = pd.DataFrame({'section': sections, 'dx': dx, 'x': x, 'r': r})

    # Step 2: Consider the apex to be at the radius local minima.
    # Step 3: Fill in the apex speeds. v = sqrt(a_y * R), where a_y = gg_radius * g
    data['AT1 speed'] = data['DT1 speed'] = np.sqrt(params['gg radius'] * g * data['r'])

    # Step 4: Fill in the speed on the straight when accelerating
    # v_i+1 = sqrt(v_i^2 + 2 * a * dx_i+1)
    at1_v_prev = 0
    for i, segment in data.iterrows():
        if segment['section'] == 'straight':
            at1_v_prev = np.sqrt(at1_v_prev**2 + 2 * params['gg radius'] * g * segment['dx'])
            data.loc[i, 'AT1 speed'] = at1_v_prev

    # Step 5: Fill in the speed when decelerating
    # v_i-1 = sqrt(v_i^2 + 2 * a * dx_i)
    dt1_v_next = data[data['section'] == 'turn 1']['DT1 speed'].iloc[-1]
    for i in range(len(data)-1, -1, -1):
        segment = data.iloc[i]
        if segment['section'] == 'straight':
            dt1_v_next = np.sqrt(dt1_v_next**2 + 2 * params['gg radius'] * g * segment['dx'])
            data.loc[i, 'DT1 speed'] = dt1_v_next
    
    # Step 6: Final speed curve
    data['final speed'] = np.minimum(data['AT1 speed'], data['DT1 speed'])

    # Step 7: Calculate lap time
    data.loc[1:, 'time delta'] = data.loc[1:, 'dx'] / data.loc[1:, 'final speed']
    data.loc[0, 'time delta'] = 0
    data['time since start'] = data['time delta'].cumsum()

    # extra data!!!!
    
    # force due to traction = coeff of friction * m * g
    data['F_traction'] = params['tire friction coeff'] * params['mass'] * g

    # RPM = (60 * drive ratio * v) / (2 * pi * tire radius)
    data['RPM'] = (60 * params['drive ratio'] * data['final speed']) / (2 * pi * params['tire radius'])

    # engine torque corresponds to RPM; we interpolate torque values from the motor torque curve
    data['engine torque'] = np.interp(data['RPM'], mtc['RPM'], mtc['torque'])

    # force motor = engine_torque * drive ratio * drivetrain eff / tire radius
    data['F_motor'] = (data['engine torque'] * params['drive ratio'] * params['drivetrain eff']) / params['tire radius']

    # force due to drag = 0.5 * air density * drag coeff * frontal area * v^2
    data['F_drag'] = 0.5 * rho * params['drag coeff'] * params['frontal area'] * data['final speed']**2

    # force applied
    data['F_applied'] = data['F_motor'] - data['F_drag'] 

    # force actual = min(F_applied, F_traction)
    data['F_actual'] = np.minimum(data['F_applied'], data['F_traction'])

    return data