import os
print('Current file:', __file__)
print('Dirname:', os.path.dirname(__file__))
print('Dirname dirname:', os.path.dirname(os.path.dirname(__file__)))
print('Project root should be:', os.path.dirname(os.path.dirname(__file__)))