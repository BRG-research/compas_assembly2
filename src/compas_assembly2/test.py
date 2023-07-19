from compas.geometry import Frame


def hello_compas_assembly2():
    """Test if compas_assembly2 is loaded

    Parameters
    ----------

    Returns
    -------
    Prints
        "Hello compas_assembly2"
    """

    frame = Frame.worldXY()
    print(frame)
    print("Hello compas and compas_assembly2 (file test.py)")
