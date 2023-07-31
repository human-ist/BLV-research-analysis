class TemporalPlotData:


  def __init__(self, 
               title: str = None,
               x: list = None, 
               y: list = None):
    self.__title: str = title
    self.__x: list = x
    self.__y: list = y


  def get_title(self) -> str:
    return self.__title
  
  def get_x(self) -> list:
    return self.__x
  
  def get_y(self) -> list:
    return self.__y
  
  def __str__(self):
        return self.__title + "; X: " + ", ".join(map(str, self.__x)) + "; Y: " + ", ".join(map(str, self.__y))