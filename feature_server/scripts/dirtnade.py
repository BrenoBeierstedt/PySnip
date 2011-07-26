from pyspades.server import block_action
from pyspades.constants import *

def apply_script(protocol, connection, config):
    def try_add_node(map, x, y, z, list):
        if x < 0 or x >= 512 or y < 0 or y >= 512 or z <= 0 or z > 63:
            return
        if map.get_solid(x, y, z):
            return
        list.append((x, y, z))
    
    class DirtGrenadeConnection(connection):
        def grenade_exploded(self, grenade):
            if self.weapon == 0:
                return connection.grenade_exploded(self, grenade)
            position = grenade.position
            x = position.x
            y = position.y
            z = position.z
            x = int(x)
            y = int(y)
            z = int(z)
            blocks = 19
            map = self.protocol.map
            list = []
            try_add_node(map, x, y, z, list)
            block_action.value = BUILD_BLOCK
            block_action.player_id = self.player_id
            color = self.block_color + (255,)
            while list:
                x, y, z = list.pop(0)
                block_action.x = x
                block_action.y = y
                block_action.z = z
                self.protocol.send_contained(block_action, save = True)
                map.set_point(x, y, z, color, user = False)
                try_add_node(map, x, y, z - 1, list)
                try_add_node(map, x, y - 1, z, list)
                try_add_node(map, x, y + 1, z, list)
                try_add_node(map, x - 1, y, z, list)
                try_add_node(map, x + 1, y, z, list)
                try_add_node(map, x, y, z + 1, list)
                blocks -= 1
                if blocks == 0:
                    break
            self.protocol.update_entities()
    
    return protocol, DirtGrenadeConnection