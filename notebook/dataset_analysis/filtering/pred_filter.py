from typing import List


class PredefinedFilter:
  "Predefined filter operation"


  def __init__(self, operation: str, column_name:str, flag:str):
    self.__operation:str = operation
    self.__type:str = 'manual'
    self.__column_name:str = column_name
    self.__flag:str = flag
    self.__removed_dois:List[str] = None
  

  def get_operation(self) -> str:
    return self.__operation
  
  def get_type(self) -> str:
    return self.__type
  
  def get_column_name(self) -> str:
    return self.__column_name
  
  def get_flag(self) -> str:
    return self.__flag
  
  def get_removed_dois(self):
    return self.__removed_dois
  
  def set_removed_dois(self, removed_dois:List[str]):
    self.__removed_dois = removed_dois

  def get_nb_removed_dois(self) -> int:
    return len(self.__removed_dois)
