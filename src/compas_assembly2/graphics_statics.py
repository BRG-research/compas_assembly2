import math


class materials:
    # modulus of elasticity - N/mm2
    modulus_of_elasticity_steel_s500 = 210000
    modulus_of_elasticity_concrete_c20_25 = 33000

    # compressive strength - N/mm2
    compressive_strength_steel_s235 = 235
    compressive_strength_steel_s355 = 335
    compressive_strength_steel_s500 = 580
    compressive_strength_concrete_c12_15 = 12
    compressive_strength_concrete_c20_25 = 20
    compressive_strength_concrete_c35_45 = 35
    compressive_strength_concrete_c55_65 = 55
    compressive_strength_timber_spruce = 20
    compressive_strength_timber_beech = 26
    compressive_strength_timber_oak = 26
    compressive_strength_timber_glulam = 22

    # tensile strength - N/mm2
    tensile_strength_steel_s235 = 235
    tensile_strength_steel_s355 = 355
    tensile_strength_steel_s500 = 580
    tensile_strength_concrete_c12_15 = 1.1
    tensile_strength_concrete_c20_25 = 1.5
    tensile_strength_concrete_c35_45 = 2.2
    tensile_strength_concrete_c55_65 = 2.9
    tensile_strength_timber_spruce = 14
    tensile_strength_timber_beech = 24
    tensile_strength_timber_oak = 26
    tensile_strength_timber_glulam = 18

    # strain mm/m
    strain_steel_s500 = 140
    strain_concrete_c20_25 = 0.06

    # density kg/m3
    density_steel_s500 = 7850
    density_steel_s235 = 8000
    density_steel_s335 = 8000
    density_concrete = 2500
    density_spruce = 450
    density_beech = 650
    density_oak = 750
    density_glulam = 500

    # safety factors
    safety_factor_gamma_dead_load = 1.35
    safety_factor_gamma_live_load = 1.5
    safety_factor_gamma_steel = 1.05
    safety_factor_gamma_reinfoced_concrete = 1.15
    safety_factor_gamma_concrete = 1.5
    safety_factor_gamma_wood = 1.7
    safety_factor_gamma_masonry = 2.0


def design_loads(live_load, dead_load):
    """Design loads are the maximum loads expected to be produced by the structure's intended use.
    live_load - loads produced by use and occupancy of the building or other structure and do not include construction or environmental loads such as wind load, snow load, rain load, earthquake load or dead load.
    dead_load - the static load caused by the weight of the contents, fixtures and fittings of a structure."""
    return live_load * materials.safety_factor_gamma_live_load + dead_load * materials.safety_factor_gamma_dead_load


def stiffness_from_force_and_length(N, delta_l):
    """Stiffness is the extent to which an object resists deformation in response to an applied force.
    N - force on the body
    delta_l - displacement produced by the force along the same degree of freedom (for instance, the change in length of a stretched spring)"""
    S = N / delta_l
    return S


def stiffness_from_area_length_and_youngs_modulus(E, A, l):
    """Stiffness is the extent to which an object resists deformation in response to an applied force.
    A - cross-sectional area of the body
    l - length of the body
    E - Young's modulus of the material"""
    S = (E * A) / l
    return S


def stress_from_force_and_area(N, A):
    """Stress is the force per unit area on a body that tends to cause it to change shape.
    N - force on the body
    A - cross-sectional area of the body"""
    sigma = N / A
    return sigma


def stress_from_youngs_modulus_and_strain(E, epsilon):
    """Stress is the force per unit area on a body that tends to cause it to change shape.
    E - Young's modulus of the material
    epsilon - strain on the body"""
    sigma = E * epsilon
    return sigma


def stress_from_youngs_modulus_and_length_change(E, l1, l0):
    """Stress is the force per unit area on a body that tends to cause it to change shape.
    E - Young's modulus of the material
    l1 - deformed length of the body
    l0 - original length of the body"""
    delta_l = l1 - l0
    sigma = (E * delta_l) / l0
    return sigma


def strain_from_length_and_original_length(l1, l0):
    """Strain is the ratio of the change in length of a body to the original length, typically expressed in parts per million.
    l1 - deformed length of the body
    l0 - original length of the body"""
    delta_l = l1 - l0
    epsilon = delta_l / l0
    return epsilon


def ultimate_limit_state(N, A, gamma_M0=1.0):
    """Ultimate limit state (ULS) is a design criterion used in engineering design which describes the ultimate load a structure must be able to sustain without suffering a structural failure.
    N - force on the body
    A - cross-sectional area of the body
    gamma_M0 - partial safety factor"""
    sigma = stress_from_force_and_area(N, A)
    return sigma / gamma_M0


def get_area_from_max_force_and_material_stree(N_max, sigma):
    """Get area from maximum force and material stress.
    N_max - maximum force on the body
    sigma - material stress"""
    return N_max / sigma


def graphic_statics_2a():
    N = 74671.0
    sigma = materials.tensile_strength_steel_s235
    A_required = get_area_from_max_force_and_material_stree(N, sigma)
    diameter = math.sqrt(A_required / math.pi) * 2
    diameter = math.ceil(diameter)
    print(diameter)
    return diameter


def diameter_from_circular_section_area(A):
    return math.sqrt(A / math.pi) * 2


def ring_area(r0, r1):
    return math.pi * (r1**2 - r0**2)


def rectangle_area(a, b):
    return a * b


def graphic_statics_2b():
    N = 74671.0
    diameter = 18
    f_material = materials.tensile_strength_steel_s355 / materials.safety_factor_gamma_steel
    A = math.pi * (diameter / 2) ** 2
    print(str(A) + " mm2")
    print(str(f_material) + " N/mm2")

    # application of the method of axial force proofing of the max load
    # proof 1 effective stress must be smaller than material stress
    # f_effective = N_design_value / A _effective <= f_material
    f_effective = N / A
    print(str(f_effective) + " N/mm2,", f_effective <= f_material)

    # proof 2 allowed material force must be bigger than max force
    # N_design_value <= N_max_allowed = A_design_value * f_material
    N_max_allowed = A * f_material

    print(str(N) + " N,", str(N_max_allowed) + " N,", N <= N_max_allowed)

    if f_effective <= f_material and N <= N_max_allowed:
        print("OK")
    else:
        print("increase element diemeter, or change material")
    return diameter


if __name__ == "__main__":
    graphic_statics_2a()
    graphic_statics_2b()
