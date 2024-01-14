from lib.image.settings_represent import SettingsRepresent
from time import time

start_time = time()
c = SettingsRepresent()
c.draw()
end_time = time()

print(f'Time elapsed: {round(end_time - start_time, 4)}ms')