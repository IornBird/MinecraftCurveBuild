# MinecraftCurveBuild
A program allows you build a Bézier curve in Minecraft
---
### What it does
Given two points `a` and `b`, it will generate a minecraft function file allowing player build a Bézier curve.

**It's for Java edition 1.21.X, and is uncertain to be working in other versions or Bedrock edition.**

![](https://github.com/IornBird/MinecraftCurveBuild/blob/main/Minecraft%20Curve%20Builder.png?raw=true)

## Usage

See [this video](https://drive.google.com/file/d/14HHKU0-pFo-eHqpVhqnCLRPQWC_eKNtd/view) to understand easier.

It's for personal use, so it's difficult to use it.
### Launch
Turn on cmd or any similar program, input:
```cmd
buildMain.py > main.mcfunction
```
You can replace `main` to another name, but it must be consisted of lowercase or underline (`_`).
- For expamle: `my_function`.

### Arguments
Please open `buildMain.py`. adjusting following variables in `main()`
```
a: begin point of the curve
b: end point of the curve
aDeg: direction from point a
bDeg: direction from point b
```
You can press F3 in Minecraft to find:
- position in `Block:`
- direction in `Facing:` (at the end of this line, for example: `90` in `Facing: west (Towards negetive X) (90.0 / 0.0)`)

Also, you can specify follwoing block types in `main()`
```
block_for_ground: block used for generate ground
block_under_rail: block user to put in center
```
If you want to build it for [high-speed rail system by flashteens](https://github.com/flashteens/FTMCRailBuilder13):
- you may set `place_arrow` to True to handle faster bulletcart.

### Functions
- `render.BZC_ANY(a, b, aDeg, bDeg)`: Curve begins and ends with any given degrees.
- `render.BZC_S(a, b, mainX)`: Curve from a to b. `mainX=True` means the curve goes mainly on x-axis direction, while offset will happen on z-axis direction.
- `render.BZC_R(a, b, xFirst)`: Curve from a to b. `xFirst=True` means the curve goes first on x-axis direction, before truning to z-axis direction.

### In Minecraft
Put the generated `.mcfunction` file in `WORLD\datapacks\AutoBuilder\data\builder\function`, for example.
> replace `WORLD` to your Minecraft world folder.
> 
> **IMPORTANT**: Ensure your datapack (assume its `AutoBuilder`) has correct structure of your game version.

Turn on Minecraft. Put a armor stand on the begin position, and add tag `build` by typing
```minecraft_function
/tag @e[type=minecraft:armor_stand,distance=..2] add build
```
**IMPORTANT**: Ensure there's only one armor stand having tag `build`.

Ensure that both begin and end position are loaded. To ensure this, you can stand between begin and end position.

Run the function (assume it's `main.mcfunction`) you put into datapack.
```minecraft_function
/function builder:main
```
The tag `build` on the armor stand will be removed after the function finished expectionally.
