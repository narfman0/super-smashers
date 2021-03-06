"""
Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024
SCREEN_TITLE = "Super Smashers"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 25

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = SCREEN_WIDTH / 3
RIGHT_VIEWPORT_MARGIN = SCREEN_WIDTH / 3
BOTTOM_VIEWPORT_MARGIN = SCREEN_HEIGHT / 4
TOP_VIEWPORT_MARGIN = SCREEN_HEIGHT / 4

PLAYER_START_X = 64
PLAYER_START_Y = 94

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.coin_list = None
        self.wall_list = None
        self.foreground_list = None
        self.background_list = None
        self.dont_touch_list = None
        self.player_list = None
        self.keys_list = None
        self.doors_list = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = None

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score
        self.score = 0

        # Where is the right edge of the map?
        self.end_of_map = 0

        # Level
        self.level = 1

        # Load sounds
        self.collect_coin_sound = arcade.load_sound("sounds/coin1.wav")
        self.jump_sound = arcade.load_sound("sounds/jump1.wav")
        self.game_over = arcade.load_sound("sounds/gameover1.wav")

    def setup(self, level):
        """ Set up the game here. Call this function to restart the game. """
        self.keys_held = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.left_pressed = False
        self.right_pressed = False

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score
        self.score = 0

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = arcade.Sprite("images/player_1/player_stand.png", CHARACTER_SCALING)
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        # --- Load in a map from the tiled editor ---

        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Coins'
        # Name of the layer that has items for foreground
        foreground_layer_name = 'Foreground'
        # Name of the layer that has items for background
        background_layer_name = 'Background'
        # Name of the layer that has items we shouldn't touch
        dont_touch_layer_name = "Don't Touch"
        # Name of the layer that has keys
        keys_layer_name = "Keys"
        # Name of the layer that has doors
        doors_layer_name = "Doors"

        # Map name
        map_name = f"map_level_{level}.tmx"
        # Read in the tiled map
        my_map = arcade.read_tiled_map(map_name, TILE_SCALING)

        # -- Walls
        # Grab the layer of items we can't move through
        map_array = my_map.layers_int_data[platforms_layer_name]

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = len(map_array[0]) * GRID_PIXEL_SIZE
        self.background_list = arcade.generate_sprites(my_map, background_layer_name, TILE_SCALING)
        self.foreground_list = arcade.generate_sprites(my_map, foreground_layer_name, TILE_SCALING)
        self.wall_list = arcade.generate_sprites(my_map, platforms_layer_name, TILE_SCALING)
        self.coin_list = arcade.generate_sprites(my_map, coins_layer_name, TILE_SCALING)
        self.doors_list = arcade.generate_sprites(my_map, doors_layer_name, TILE_SCALING)
        self.dont_touch_list = arcade.generate_sprites(my_map, dont_touch_layer_name, TILE_SCALING)
        self.keys_list = arcade.generate_sprites(my_map, keys_layer_name, TILE_SCALING)

        self.end_of_map = (len(map_array[0]) - 1) * GRID_PIXEL_SIZE

        # --- Other stuff
        # Set the background color
        if my_map.backgroundcolor:
            arcade.set_background_color(my_map.backgroundcolor)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             GRAVITY)

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        self.wall_list.draw()
        self.background_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.keys_list.draw()
        self.player_list.draw()
        self.foreground_list.draw()
        self.dont_touch_list.draw()
        self.doors_list.draw()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.BLACK, 18)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        if key == arcade.key.V:
            self.complete_level()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

    def complete_level(self):
         # Advance to the next level
        self.level += 1

        # Load the next level
        self.setup(self.level)

        # Set the camera to the start
        self.view_left = 0
        self.view_bottom = 0
        changed_viewport = True

    def update(self, delta_time):
        """ Movement and game logic """
        self.player_sprite.change_x -= 1
        if self.left_pressed:
            self.velocity_x = min(max(-PLAYER_MOVEMENT_SPEED, self.velocity_x - 1), PLAYER_MOVEMENT_SPEED)
        if self.right_pressed:
            self.velocity_x = min(max(-PLAYER_MOVEMENT_SPEED, self.velocity_x + 1), PLAYER_MOVEMENT_SPEED)
        if not self.right_pressed and not self.left_pressed:
            if self.velocity_x > 0:
                self.velocity_x -= 1
            elif self.velocity_x < 0:
                self.velocity_x += 1
        self.player_sprite.change_x = self.velocity_x

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.score += 1

        # Track if we need to change the viewport
        changed_viewport = False

        # Did the player fall off the map?
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
            arcade.play_sound(self.game_over)

        # Did the player touch something they should not?
        if arcade.check_for_collision_with_list(self.player_sprite, self.dont_touch_list):
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
            arcade.play_sound(self.game_over)

        # Did the player touch a key?
        keys_collided = arcade.check_for_collision_with_list(self.player_sprite, self.keys_list)
        for key in keys_collided:
            key.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.keys_held += 1
            
        # Did the player touch a door?
        doors_collided = arcade.check_for_collision_with_list(self.player_sprite, self.doors_list)
        for door in doors_collided:
            if self.keys_held > 0:
                door.remove_from_sprite_lists()
                arcade.play_sound(self.collect_coin_sound)
                self.keys_held -= 1

        # See if the user got to the end of the level
        if self.player_sprite.center_x >= self.end_of_map:
            self.complete_level()

        # --- Manage Scrolling ---

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed_viewport = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed_viewport = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_viewport = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed_viewport = True

        if changed_viewport:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    """ Main method """
    window = MyGame()
    window.setup(window.level)
    arcade.run()


if __name__ == "__main__":
    main()
