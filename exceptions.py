class PromptNotInformed(Exception):  
  def __init__(self, message="Prompt is not informed"):
    super().__init__(message)

class SizeNotInformed(Exception):
  def __init__(self, message="Size is not informed"):
    super().__init__(message)