import amulet
import numpy
from amulet.api.block import Block


def _main():
    chunk_count = 0
    count = 1
    universal_block_count = 0
    find_block_matches = []

    print("ワールドのディレクトリパスを入力してください。")
    directory = input()
    world = amulet.load_level(directory)

    all_dimension_name = ""
    # 処理を除外するディメンションの選択
    for dimension in world.dimensions:
        all_dimension_name += dimension + " "

    print("このワールドの全ディメンション名")
    print(all_dimension_name)
    print("処理を除外したいディメンションがある場合は、ディメンション名を入力してください。")
    print("複数ある場合はカンマ「,」区切りで入力してください")
    exclude_dimension = input()
    exclude_dimension_list = exclude_dimension.split(",")

    print("削除するブロックを入力してください。 例 minecraft:water[level=0]")
    find_block_str = input()
    find_block = Block.from_string_blockstate(find_block_str)
    air_block = world.block_palette.get_add_block(Block("minecraft", "air"))

    # 全てのディメンションのチャンク数を取得
    for dimension in world.dimensions:
        if dimension not in exclude_dimension_list:
            chunk_count += len(list(world.all_chunk_coords(dimension)))

    print("ブロック削除プラグイン実行")
    print("総検索チャンク数:" + str(chunk_count))
    print("----------検索開始----------")

    for dimension in world.dimensions:
        if dimension in exclude_dimension_list:
            continue

        for cx, cz in world.all_chunk_coords(dimension):
            chunk = world.get_chunk(cx, cz, dimension)

            # チャンクで使用されているブロックのパレットに、今までループしたチャンクのパレットにないブロックがある場合
            if universal_block_count < len(chunk.block_palette):
                for universal_block_id in range(
                        universal_block_count, len(chunk.block_palette)
                ):
                    # ブロックを取得
                    version_block = world.block_palette[universal_block_id]

                    # ブロックが検索対象のブロックと一致する場合
                    if _check_block(find_block, version_block):
                        find_block_matches.append(universal_block_id)

                # パレットのブロック数を更新
                universal_block_count = len(chunk.block_palette)

            blocks = chunk.blocks[chunk.blocks.slice_x, chunk.blocks.slice_y, chunk.blocks.slice_z]
            blocks[numpy.isin(blocks, find_block_matches)] = air_block
            chunk.blocks[chunk.blocks.slice_x, chunk.blocks.slice_y, chunk.blocks.slice_z] = blocks
            chunk.changed = True
            count += 1

            print(dimension + " " + str(count) + "/" + str(chunk_count))

            if count % 1000 == 0:
                print("途中経過を保存中...")
                world.save()
                world.purge()

    world.save()
    world.close()
    return 0


def _check_block(source: Block, target: Block):
    if source.base_name != target.base_name or not all(
            target.properties.get(prop) in ["*", val.to_snbt()]
            for prop, val in source.properties.items()
    ):
        return False


if __name__ == '__main__':
    _main()
