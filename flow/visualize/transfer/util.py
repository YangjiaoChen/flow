"""Definitions of transfer classes."""
from copy import deepcopy

from flow.core.params import InFlows
from examples.exp_configs.rl.multiagent.multiagent_i210 import VEH_PER_HOUR_BASE_119257914, \
    VEH_PER_HOUR_BASE_27414345, VEH_PER_HOUR_BASE_27414342


def make_inflows(pr=0.1, fr_coef=1.0, departSpeed=20, on_ramp=False, apr=0.0):
    """Generate inflows object from parameters. Uses default inflows from multiagent_i210.

    Keyword Arguments:
    -----------------
        pr {float} -- [AV Penetration Rate] (default: {0.1})
        fr_coef {float} -- [Scale flow rate by] (default: {1.0})
        departSpeed {int} -- [Initial speed of all flows] (default: {20})

    Returns
    -------
        [Inflows] -- [Inflows parameter object]

    """
    inflow = InFlows()
    # main highway
    assert pr < 1.0, "your penetration rate is over 100%"

    assert apr < 1.0, "Aggressive driver rate should be below 100%"
    assert apr + pr < 1.0, "Combined rate should be less than 100%"

    all_inflows = []

    inflow_119257914 = dict(veh_type="human",
                            edge="119257914",
                            vehs_per_hour=VEH_PER_HOUR_BASE_119257914 *
                            (1 - (pr + apr)) * fr_coef,
                            # probability=1.0,
                            departLane="random",
                            departSpeed=departSpeed)
    all_inflows.append(inflow_119257914)

    if pr > 0.0:
        inflow_119257914_av = dict(veh_type="av",
                                   edge="119257914",
                                   vehs_per_hour=int(VEH_PER_HOUR_BASE_119257914 * pr * fr_coef),
                                   # probability=1.0,
                                   departLane="random",
                                   departSpeed=departSpeed)
        all_inflows.append(inflow_119257914_av)

    if apr > 0.0:
        inflow_119257914_aggro = dict(veh_type="aggressive",
                                      edge="119257914",
                                      vehs_per_hour=int(VEH_PER_HOUR_BASE_119257914 *
                                                        apr * fr_coef),
                                      # probability=1.0,
                                      departLane="random",
                                      departSpeed=departSpeed)
        all_inflows.append(inflow_119257914_aggro)

    if on_ramp:
        inflow_27414345 = dict(veh_type="human",
                               edge="27414345",
                               vehs_per_hour=VEH_PER_HOUR_BASE_27414345 *
                               (1 - (pr + apr)) * fr_coef,
                               departLane="random",
                               departSpeed=departSpeed)
        all_inflows.append(inflow_27414345)
        if pr > 0.0:
            inflow_27414342 = dict(veh_type="human",
                                edge="27414342#0",
                                vehs_per_hour=VEH_PER_HOUR_BASE_27414342 * pr * fr_coef,
                                departLane="random",
                                departSpeed=departSpeed)
            all_inflows.append(inflow_27414342)

    for inflow_def in all_inflows:
        inflow.add(**inflow_def)

    return inflow


class BaseTransfer:
    """Base Transfer class."""

    def __init__(self):
        self.transfer_str = "Base"
        pass

    def flow_params_modifier_fn(self, flow_params, clone_params=True):
        """Return modified flow_params.

        Arguments:
        ---------
            flow_params {[flow_params_dictionary]} -- [flow_params]
        """
        if clone_params:
            flow_params = deepcopy(flow_params)

        return flow_params

    def env_modifier_fn(self, env):
        """Modify the env before rollouts are run.

        Arguments:
        ---------
            env {[I210MultiEnv]} -- [Env to modify]
        """
        pass


class InflowTransfer(BaseTransfer):
    """Modifies the inflow of i210 env."""

    def __init__(self, penetration_rate=0.1, flow_rate_coef=1.0, departSpeed=20, aggressive_driver_penetration=0.0):
        super(InflowTransfer, self).__init__()
        self.penetration_rate = penetration_rate
        self.flow_rate_coef = flow_rate_coef
        self.departSpeed = departSpeed
        self.aggressive_driver_penetration = aggressive_driver_penetration

        self.transfer_str = "{:0.2f}_pen_{:0.2f}_flow_rate_coef_{:0.2f}_depspeed_{:0.2f}_apr".format(
            penetration_rate, flow_rate_coef, departSpeed, aggressive_driver_penetration)

    def flow_params_modifier_fn(self, flow_params, clone_params=True):
        """See Parent."""
        if clone_params:
            flow_params = deepcopy(flow_params)

        flow_params['net'].inflows = make_inflows(pr=self.penetration_rate, fr_coef=self.flow_rate_coef,
                                                  departSpeed=self.departSpeed, apr=self.aggressive_driver_penetration)

        return flow_params


def inflows_range(penetration_rates=0.1, flow_rate_coefs=1.0, departSpeeds=20.0, aggressive_driver_penetrations=0.0):
    """Generate inflow objects given penetration_rates, flow_rates, and depart speeds.

    Keyword Arguments:
    -----------------
        penetration_rates {float | list of floats} -- [single, or multiple penetration rates] (default: {0.1})
        flow_rate_coefs {float | list of floats} -- [single, or multiple flow rate coefficient] (default: {1.0})
        departSpeeds {float | list of floats} -- [single, or multiple depart speeds] (default: {20.0})

    Yields
    ------
        [InflowTransfer] -- [Transfer object]
    """
    if not hasattr(penetration_rates, '__iter__'):
        penetration_rates = [penetration_rates]
    if not hasattr(flow_rate_coefs, '__iter__'):
        flow_rate_coefs = [flow_rate_coefs]
    if not hasattr(departSpeeds, '__iter__'):
        departSpeeds = [departSpeeds]
    if not hasattr(aggressive_driver_penetrations, '__iter__'):
        aggressive_driver_penetrations = [aggressive_driver_penetrations]

    for departSpeed in departSpeeds:
        for penetration_rate in penetration_rates:
            for flow_rate_coef in flow_rate_coefs:
                for aggressive_driver_penetration in aggressive_driver_penetrations:
                    yield InflowTransfer(penetration_rate=penetration_rate, flow_rate_coef=flow_rate_coef,
                                         departSpeed=departSpeed, aggressive_driver_penetration=aggressive_driver_penetration)