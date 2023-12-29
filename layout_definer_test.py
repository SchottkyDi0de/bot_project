# from PIL import Image, ImageDraw

# class StatsBlockSize:
#     main_stats = 240
#     rating_stats = 260
#     full_tank_stats = 260
#     short_tank_stats = 200


# class BlockOffsets:
#     first_indent = 80
#     block_indent = 20
#     horizontal_indent = 55
    

# class ImageSize:
#     max: int = 1350

# class LayoutDefiner:
#     def __init__(self, session_data: dict = {'tank_stats': 1, 'rating_count': 0}) -> None:
#         self.data = session_data
#         self.blocks = 1
#         self.small_blocks = 0
        
#         self.include_rating = True if session_data['rating_count'] > 0 else False
#         self.tanks_count = 0
        
#     def _calculate_stats_blocks(self) -> None:
#         self.tanks_count = self.data['tank_stats']
        
#         if self.include_rating:
#             self.blocks += 1
        
#         if self.tanks_count >= 1:
#             self.blocks += 1
            
#         if self.tanks_count >= 2:
#             self.blocks += 1
        
#         if self.tanks_count >= 3:
#             if self.include_rating:
#                 self.small_blocks = 2
#                 self.blocks -= 1
#             else:
#                 self.blocks += 1
                
#         if self.tanks_count >= 4:
#             if not self.include_rating:
#                 self.small_blocks = 2
#                 self.blocks -= 1
                
#     def _calculate_image_size(self) -> None:
#         if self.blocks == 3 and self.small_blocks == 2:
#             self.image_size = 1350
#             return
        
#         self.image_size = (
#             BlockOffsets.first_indent + StatsBlockSize.main_stats +
#             BlockOffsets.block_indent * (self.blocks + self.small_blocks) +
#             StatsBlockSize.full_tank_stats * (self.blocks - 1) +
#             StatsBlockSize.short_tank_stats * self.small_blocks
#         )

#     def _prepare_background(self):
#         self.layout_map = Image.new(
#             'RGBA',
#             (700, self.image_size),
#             (0, 0, 0, 255)
#         )

#     def create_rectangle_map(self) -> Image.Image:
#         self._calculate_stats_blocks()
#         self._calculate_image_size()
#         self._prepare_background()
        
#         print(f'img height: {self.image_size} blocks: {self.blocks} small: {self.small_blocks}')
#         drawable_layout = ImageDraw.Draw(self.layout_map)
#         current_offset = BlockOffsets.first_indent
#         first_block = True

#         for _ in range(self.blocks):
#             drawable_layout.rounded_rectangle(
#                 (
#                     BlockOffsets.horizontal_indent, 
#                     current_offset,
#                     700 - BlockOffsets.horizontal_indent,
#                     (StatsBlockSize.main_stats if first_block else StatsBlockSize.full_tank_stats) + current_offset
#                 ),
#                 fill='white',
#                 radius=10
#             )
#             if first_block:
#                 current_offset += StatsBlockSize.main_stats
#             else:
#                 current_offset += StatsBlockSize.full_tank_stats
                
#             current_offset += BlockOffsets.block_indent
#             first_block = False
         
#         if self.small_blocks > 0:
#             for _ in range(self.small_blocks):
#                 drawable_layout.rounded_rectangle(
#                     (
#                         BlockOffsets.horizontal_indent, 
#                         current_offset, 
#                         700 - BlockOffsets.horizontal_indent,
#                         current_offset + StatsBlockSize.short_tank_stats
#                     ),
#                     fill='white',
#                     radius=10
#                 )
#                 current_offset += StatsBlockSize.short_tank_stats + BlockOffsets.block_indent
                
#         self.layout_map.show()

    
class LayoutDefiner:
    def __init__(self) -> None:
        self.blocks_map = {}
        self.blocks = 1
        self.small_blocks = 0
        self.max_fullstats_blocks = 4
        self.max_short_stats_blocks = 2
        self.include_rating = False
        
    def _calculate_stats_blocks(self, data: dict) -> None:
        tanks_count = len(data['tank_stats'])
        print(tanks_count)
        self.include_rating = True if data['rating_diff']['battles'] > 0 else False
        
        if self.include_rating:
            self.blocks += 1
            
        if (self.blocks + tanks_count) == self.max_fullstats_blocks:
            self.blocks = 4
            self.small_blocks = 0
            return
            
        if (self.blocks + tanks_count) < self.max_fullstats_blocks:
            self.blocks += tanks_count
            return
            
        if (self.blocks + tanks_count) > self.max_fullstats_blocks:
            self.blocks = self.max_fullstats_blocks - 1
            self.small_blocks = self.max_short_stats_blocks
            return
            
    def calculate_block_map(self):
        for i in range(self.blocks + self.small_blocks):
            if i <= 1:
                self.blocks_map.setdefault(0, 0)
            if 1 == 2:
                self.blocks_map.setdefault(1, 2)

        
ld = LayoutDefiner()
ld._calculate_stats_blocks({'tank_stats': [1], 'rating_diff': {'battles': 1}})
print(f'blocks: {ld.blocks} small: {ld.small_blocks}')