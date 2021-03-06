import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
# Add Gnosis module to python paths
sys.path.append(os.path.realpath(os.path.join(script_dir, '..', '..')))

# noinspection PyPep8
from EVE_Gnosis.simulations.capacitor import Capacitor
# noinspection PyPep8
from EVE_Gnosis.formulas.formulas import Formulas


def build_module_list():
    module_list = []

    '''
    Note that not all modules effect cap.  Even though the full fit is below,most of the modules have no impact on cap.

    [Deimos, LCB Deimos]

    Reactive Armor Hardener
    Energized Adaptive Nano Membrane II
    Energized Adaptive Nano Membrane II
    Energized Explosive Membrane II
    Magnetic Field Stabilizer II
    Medium Armor Repairer II

    50MN Quad LiF Restrained Microwarpdrive
    Stasis Webifier II
    Small Electrochemical Capacitor Booster I, Navy Cap Booster 100
    Large Compact Pb-Acid Cap Battery

    Heavy Ion Blaster II, Void M
    Heavy Ion Blaster II, Void M
    Heavy Ion Blaster II, Void M
    Heavy Ion Blaster II, Void M
    Heavy Ion Blaster II, Void M

    Medium Auxiliary Nano Pump I
    Medium Auxiliary Nano Pump I
    '''
    # Deimos Modules

    turret_slots = 5
    turret_count = 0
    while turret_count < turret_slots:
        module_list.append(
            {
                'Amount': -3.06403125,
                'CycleTime': 2899.8000000000006,
                'ReloadTime': 5000,
                'Charges': 120,
            }
        )  # 5 x Heavy Ion Blaster II with Void ammo
        turret_count += 1

    module_list.append(
        {
            'Amount': -135,
            'CycleTime': 10000,
        }
    )  # 50mn Quad LiF Restrained Microwarpdrive

    module_list.append(
        {
            'Amount': -4.5,
            'CycleTime': 5000,
        }
    )  # Stasis Webifier II

    module_list.append(
        {
            'Amount': 100,
            'CycleTime': 12000,
            'ReloadTime': 10000,
            'Charges': 4,
            'DelayTime': 10000,  # Delay running this right away, so we don't waste charges
        }
    )  # Small Electrochemical Capacitor Booster I

    module_list.append(
        {
            'Amount': -10.5,
            'CycleTime': 5000,
        }
    )  # Reactive Armor Hardener

    module_list.append(
        {
            'Amount': -160,
            'CycleTime': 9000,
            'ArmorRepair': 657.761137524,
        }
    )  # Medium Armor Repairer II

    return module_list


def capacitor_amount():
    value = 2830
    return value


def capacitor_recharge():
    value = 168750
    return value


def simulation_matrix():
    matrix = Capacitor.capacitor_time_simulator(build_module_list(),
                                                capacitor_amount(),
                                                capacitor_recharge())
    return matrix


def regen_matrix():
    matrix = Formulas.capacitor_shield_regen_matrix(capacitor_amount(), capacitor_recharge())
    return matrix


def regen_peak():
    matrix = regen_matrix()
    high_water_percent = 0
    high_water_delta = 0
    for item in matrix:
        if high_water_delta < item['DeltaAmount']:
            high_water_percent = item['Percent']
            high_water_delta = item['DeltaAmount']

    return {'PeakDelta': high_water_delta, 'PeakPercent': high_water_percent}


def test_peak_capacitor_regen():
    # Check that the peak capacitor regen is the expected percent and delta
    expected_capacitor_percent = 0.24
    expected_capacitor_delta = 41.92167610022477

    peak = regen_peak()

    assert expected_capacitor_percent == peak['PeakPercent']
    assert expected_capacitor_delta == peak['PeakDelta']


def test_simulation():
    expected_cached_run_count = 467
    expected_low_water_mark = 1316.76629410617
    expected_time = 530999.9999999995
    expected_capacitor_tick_0_percent = 0.89
    expected_capacitor_tick_0_time = 0
    expected_capacitor_tick_7_percent = 0.82
    expected_capacitor_tick_7_time = 11599.200000000003
    expected_capacitor_tick_8_percent = 0.83
    expected_capacitor_tick_8_time = 14499.000000000004
    expected_capacitor_tick_max_run_percent = 0.57
    expected_capacitor_tick_max_run_time = 601999.9999999997
    expected_armor_repair_amount_tick_0 = 657.761137524
    expected_armor_repair_amount_tick_225 = 657.761137524
    expected_failed_to_run_modules = False

    matrix = simulation_matrix()

    cached_runs_count = 0
    for _ in matrix['Cached Runs']:
        cached_runs_count += 1

    assert expected_cached_run_count == cached_runs_count
    assert expected_low_water_mark == matrix['Stability']['LowWaterMark']
    assert expected_time == matrix['Stability']['LowWaterMarkTime']
    assert expected_capacitor_tick_0_percent == matrix['Cached Runs'][0]['Capacitor Percentage']
    assert expected_capacitor_tick_0_time == matrix['Cached Runs'][0]['Current Time']
    assert expected_capacitor_tick_7_percent == matrix['Cached Runs'][7]['Capacitor Percentage']
    assert expected_capacitor_tick_7_time == matrix['Cached Runs'][7]['Current Time']
    assert expected_capacitor_tick_8_percent == matrix['Cached Runs'][8]['Capacitor Percentage']
    assert expected_capacitor_tick_8_time == matrix['Cached Runs'][8]['Current Time']
    assert expected_capacitor_tick_max_run_percent == matrix['Cached Runs'][cached_runs_count - 1]['Capacitor Percentage']
    assert expected_capacitor_tick_max_run_time == matrix['Cached Runs'][cached_runs_count - 1]['Current Time']
    assert expected_armor_repair_amount_tick_0 == matrix['Cached Runs'][0]['Armor Reps']
    assert expected_armor_repair_amount_tick_225 == matrix['Cached Runs'][225]['Armor Reps']
    assert expected_failed_to_run_modules == matrix['Stability']['FailedToRunModules']
