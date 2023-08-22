from compas.geometry import Frame
import compas_assembly2


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
    print("Hello compas and compas_assembly2")
    print(compas_assembly2.__version__)
