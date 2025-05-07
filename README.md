# MinecraftCurveBuild
A program allows you build a Bézier curve in Minecraft
---
### What it does
Given to points a and b, it will generate a minecraft function file allows player build a Bézier curve.
It's for Java edition, and uncertain to use it for Bedrock edition

## Usage
It's for personal use, so it's difficult to use it.
### Launch
Turn on cmd or any similar program, input:
```cmd
python buildMain.py 1 > main.mcfunction
```
You can replace `1` to anything, since it doesn't matters.

### Arguments
Please open `buildMain.py`. adjusting following variables in `main()`
```
a: begin of the curve
b: end of the curve
aDeg: direction from point a
bDeg: direction from point b
```

### Functions
`render.BZC_ANY(a, b, aDeg, bDeg)`: Curve begin and end with any degree.
`render.BZC_S(a, b, mainX)`: Curve from a to b. `mainX=True` means the curve goes mainly on x-axis, while offset will happen on z-axis.
`render.BZC_R(a, b, xFirst)`: Curve from a to b. `xFirst=True` means the curve goes first on x-axis, before truning to z-axis.

### In Minecraft
> Put the generated `.mcfunction` file in `WORLD\datapacks\AutoBuilder\data\builder\function`, for example.
> > replace `WORLD` to your Minecraft world folder.
> > **IMPORTANT** Ensure your datapack has correct structure of your game version.
>
> Turn on Minecraft. Put a armor stand on the begin position (press F3 to check), and add tag `build` by typing
> ```minecraft_function
> /tag @e[type=minecraft:armor_stand,distance=..2] add build
> ```
> Stand between begin and end position if two points are far. Run the function (assume it's `main.mcfunction`) you put into datapack.
> ```minecraft_function
> /function builder:main
> ```
