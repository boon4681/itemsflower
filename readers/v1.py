import json
import re

from src.source import Source
from src.color import ColorMap, to_hex


class Reader:
    def __init__(self, source: Source):
        self.source = source

    def read(self, version: str,fetch:bool=True):
        print(version)
        if(fetch): self.source.fetch(version)
        location = self.source.make(version)
        classes = [
            'net.minecraft.client.color.block.BlockColors',
            'net.minecraft.world.level.block.Blocks',
            'net.minecraft.world.item.Items',
            'net.minecraft.client.color.item.ItemColors',
            'net.minecraft.world.level.FoliageColor',
            'net.minecraft.client.renderer.BiomeColors',
            'net.minecraft.world.level.GrassColor',
            'net.minecraft.world.item.SpawnEggItem'
        ]
        infos = self.source.get_classes(version, classes)
        foliage_colors_class = infos['net.minecraft.world.level.FoliageColor']
        blocks_class = infos['net.minecraft.world.level.block.Blocks']
        items_class = infos['net.minecraft.world.item.Items']
        block_colors_class = infos['net.minecraft.client.color.block.BlockColors']
        item_colors_class = infos['net.minecraft.client.color.item.ItemColors']
        biome_colors_class = infos['net.minecraft.client.renderer.BiomeColors']
        grass_colors_class = infos['net.minecraft.world.level.GrassColor']
        spawn_eggs_class = infos['net.minecraft.world.item.SpawnEggItem']
        foliage_colors_class = infos['net.minecraft.world.level.FoliageColor']
        blocks_class = infos['net.minecraft.world.level.block.Blocks']
        items_class = infos['net.minecraft.world.item.Items']
        block_colors_class = infos['net.minecraft.client.color.block.BlockColors']
        item_colors_class = infos['net.minecraft.client.color.item.ItemColors']
        biome_colors_class = infos['net.minecraft.client.renderer.BiomeColors']
        grass_colors_class = infos['net.minecraft.world.level.GrassColor']
        spawn_eggs_class = infos['net.minecraft.world.item.SpawnEggItem']

        self.source.decompile_classes(version, infos)
        self.colormap = ColorMap(location)
        foliage_colors = read_foliage_colors(
            self.source.read_java(version, foliage_colors_class))

        blocks = read_blocks(self.source.read_java(version, blocks_class))

        block_colors = read_colors(
            self.colormap,
            foliage_colors,
            blocks,
            foliage_colors_class,
            grass_colors_class,
            biome_colors_class,
            self.source.read_java(version, block_colors_class)
        )
        items_colors = read_colors(
            self.colormap,
            foliage_colors,
            blocks,
            foliage_colors_class,
            grass_colors_class,
            biome_colors_class,
            self.source.read_java(version, item_colors_class)
        )

        spawn_egg_colors = read_spawn_egg_colors(
            spawn_eggs_class,
            self.source.read_java(version, items_class)
        )
        colors = set(block_colors).union(set(items_colors))
        items_colors['lily_pad'] = to_hex(7455580)

        with open(location.parsed.joinpath('spawn_eggs.json'), 'w') as f:
            f.write(json.dumps(spawn_egg_colors))
        with open(location.parsed.joinpath('items.json'), 'w') as f:
            f.write(json.dumps(items_colors))
        with open(location.parsed.joinpath('blocks.json'), 'w') as f:
            f.write(json.dumps(block_colors))
        with open(location.parsed.joinpath('all.json'), 'w') as f:
            f.write(
                json.dumps(
                    {
                        'spawn_eggs': spawn_egg_colors,
                        'items': items_colors,
                        'blocks': block_colors
                    }
                )
            )

        return {
            'spawn_eggs': spawn_egg_colors,
            'items': items_colors,
            'blocks': block_colors
        }


def read_foliage_colors(text):
    matches = re.finditer(
        r'public static int (\w+)\(\) {(?:[\W]*)return (\d+);(?:[\W]*)}',
        text,
        re.MULTILINE
    )
    result = {}
    for i in matches:
        result[i.group(1)] = i.group(2)
    return result


def read_blocks(text: str):
    blocks = {}
    for line in text.split('\n'):
        matches = re.match(
            r"(?:\s+)public static final \w+ (\w+).+\"(\w+)", line)
        if(matches):
            blocks[matches.group(1)] = matches.group(2)
    return blocks


def read_items(text: str):
    items = {}
    for line in text.split('\n'):
        matches = re.match(
            r"(?:\s+)public static final \w+ (\w+).+\"(\w+)", line)
        if(matches):
            items[matches.group(1)] = matches.group(2)
    return items


def read_spawn_egg_colors(spawn_egg_class, text: str):
    items = {}
    for line in text.split('\n'):
        matches = re.match(
            f'(?:\s+)public static final \w+ (\w+).+\"(\w+).+({spawn_egg_class["name"]}\(.+)', line)
        if(matches):
            primary_color, secondary_color = re.findall(
                r'(\d+)', matches.group(3))
            items[matches.group(2)] = {
                'primary_color': to_hex(int(primary_color)),
                'secondary_color': to_hex(int(secondary_color))
            }
    return items


def read_colors(colormap, foliage_colors, items, foliage_class, grass_colors_class, biome_colors_class, text):
    matches = re.finditer(
        f'({foliage_class["name"]}|{grass_colors_class["name"]}|{biome_colors_class["name"]}).(\w)\(([^()]*)\)(?:.+)(?:[\r\n])?'+'\{ (.+) \}',
        text,
        re.MULTILINE
    )
    colors = {}
    for i in matches:
        if(i.group(1) == foliage_class["name"]):
            color = to_hex(int(foliage_colors[i.group(2)]))
        if(i.group(1) == grass_colors_class["name"]):
            parsed_input = list(map(lambda x: float(x), re.findall(
                r'((?:[0-9]|[1-9][0-9]+)\.[0-9]+)', i.group(3))))
            color = str(colormap.get(
                'grass', parsed_input[0], parsed_input[1]))
        if(i.group(1) == biome_colors_class["name"]):
            for j in i.group(4).replace(' ', '').split(','):
                print(f"Ignored {items[j.split('.')[1]]}")
            continue
        for j in i.group(4).replace(' ', '').split(','):
            colors[items[j.split('.')[1]]] = color
    return colors
