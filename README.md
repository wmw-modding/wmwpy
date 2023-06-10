# wmwpy
Python module for working with Where's My...? game files.

<!-- Note: using https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/ for distributing.-->

This is being used in [Where's My Editor](https://github.com/wmw-modding/wheres-my-editor), a level editor for the Where's My...? series.


# Table of contents

- [wmwpy](#wmwpy)
- [Table of contents](#table-of-contents)
- [Installation](#installation)
- [Usage](#usage)
  - [Get game folder](#get-game-folder)
  - [Loading the game](#loading-the-game)
  - [Main classes](#main-classes)
    - [Level](#level)
      - [Challenges](#challenges)
    - [Object](#object)
- [Building package](#building-package)
- [Building docs](#building-docs)
- [Credits](#credits)

# Installation
To install `wmwpy`, run

```
pip install wmwpy
```

or

```
python -m pip install wmwpy
```

You can also install it from the source, which may be needed because it is frequently being updated, although you need to make sure `git` is installed.

```
pip install wmwpy@git+https://github.com/wmw-modding/wmwpy
```

# Usage
## Get game folder
To get started, you need to have a Where's My Water? game folder, either an extracted apk, ipa, or on a rooted / jailbroken device (for editing the game files directly). The game must be extracted like this.

```
- root
 - assets
  - ...
```
 
The assets folder can be specified in `wmwpy`.

## Loading the game
Start by loading the game inside `wmwpy`

```python
import wmwpy
game = wmwpy.load('game/wmw')
```

You can specify the assets folder

```python
game = wmwpy.load('game/wmw', assets = '/assets')
```

You can set `assets = '.'` if you have the gamepath (first parameter) set to the assets folder (such as on a rooted / jailbroken device).

Alternately, you can specify the platform.

```python
game = wmwpy.load('game/wmw', platform = 'android')
```

This automatically sets the assets folder to what it is on the platform.

| Platform | assets folder |
| -------- | ------------- |
| android  | /assets       |
| ios      | /Content      |

You can also specify the game, which sets things up for that game.

```python
game = wmwpy.load('game/wmp', game = 'WMP')
```

Currently all the games are

| Game                                   | Code      |
| ----                                   | ----      |
| Where's My Water?                      | 'WMW'     |
| Where's My Water? Free                 | 'WMWF'    |
| Where's My Perry?                      | 'WMP'     |
| Where's My Perry? Free                 | 'WMPF'    |
| Where's My Mickey?                     | 'WMM'     |
| Where's My Mickey? XL                  | 'WMMXL'   |
| Where's My Mickey? Free                | 'WMMF'    |
| Where's My XiYangYang?                 | 'WMXYY'   |
| Where's My Water? Featuring XiYangYang | 'WMWFXYY' |
| Where's My Water? 2                    | 'WMW2'    |
| Where's My Holiday?                    | 'WMH'     |
| Where's My Valentine?                  | 'WMV'     |
| Where's My Summer?                     | 'WMS'     |

You can also specify the base assets path, the folder within the assets folder that contains all the assets. For example, Where's My Perry? has all the data within `/assets/Perry`.

```python
game = wmwpy.load('game/wmp', baseassets = '/Perry')
```

Each game has the database in a different location, so you can specify it.

```python
game = wmwpy.load('game/wmp', db = '/Perry/Data/perry.db')
```

Since Where's My Water? 2 uses a profile instead of a database for the save data, you can also specify that.

```python
game = wmwpy.load('game/wmw2', profile = '/Water/Data/factory_profile.json')
```

You can also provide a function to be called during the loading, so you can keep track of the current progress, e.g. in a gui application with a progress bar.

```python
game = wmwpy.load('game/wmw', load_hook = lambda progress, text, max : print(f'({progress}/{max}) {text}'))
```

The inputs for the function are
```
(
   progress : int,
   text : str,
   max : int,
)
```

Once you're done editing all the files, you need to dump the all the assets.

```python
game.dump()
```

This will save all the files in the game inside the assets folder. You can customize this if you want them saved in a different location.

```python
game.dump(folder = 'path/to/output')
```

## Main classes

### Level
To load a level from within a game, use the `.Level()` method.

```python
level = game.Level('first_dig')
```

The first input can be the name of a level inside the `/Levels` folder (`first_dig`), an absolute path to the level (`/Levels/first_dig`), or the path to an xml file (`/Levels/first_dig.xml`).

You can also specify the xml and image separately.

```python
level = game.Level(xmlPath = '/Levels/first_dig.xml', imagePath = '/Levels/first_dig.png')
```

Some levels include objects that wmwpy fails to load, so you can use the `ignore_errors` parameter to ignore them.

```python
level = game.Level('first_dig', ignore_errors = True)
```

You can also use the HD or TabHD textures for the objects.

```python
level = game.Level('first_dig', HD = True, TabHD = True)
```

If both are specified, TabHD will get priority. If it can't load TabHD textures. See hierarchy.

```
- TabHD
 - HD
  - Low Quality
```

You can also provide a function to run while loading to see the current progress.

```python
level = game.Level('first_dig', load_callback = lambda progress, text, max : print(f'({progress}/{max}) {text}'))
```

The inputs for the function are
```
(
   progress : int,
   text : str,
   max : int,
)
```

The objects in the level are all accessible in a list

```python
>> level.objects
[
   <wmwpy.classes.object.Object object at 0x000001C7627FE850>,
   ...
]
```

See [Object](#Object)

The level properties are also accessible as a dictionary

```python
>> level.properties
{'HeavyIntro': '1'}
```

WMW2 challenges are also accessible in a list

```python
>> level.challenges
[<wmwpy.classes.level.Level.Challenge object at 0x000001C72176ADD0>]
```

Once you're finished editing the level, you can get the xml.

```python
xml = level.export(filename = '/Levels/first_dig.xml',)
```

This returns the xml file as `bytes`, but also saves the file to the game filesystem.

#### Challenges
Each challenge has requirements in a dictionary
```python
>> level.challenges[0].requirements
{
    'WinWait': {
        'seconds': ''
    },
    'Duck': {
        'count': '2'
    }
}
```

### Object
To load an object within a game, use the `.Object()` method.

```python
obj = game.Object('/Objects/broken_pipe.hs')
```

You can also use the HD or TabHD textures for the objects.

```python
level = game.Level('first_dig', HD = True, TabHD = True)
```

If both are specified, TabHD will get priority. If it can't load TabHD textures. See hierarchy.

```
- TabHD
 - HD
  - Low Quality
```

An object has many properties

```python
>> obj.properties
{
    'Type' : 'spout',
    'SpoutType' : 'DrainSpout',
    'Goal' : '1',
    'GoalPreset', : 'Swampy',
}
```

An object also has many [Sprites](#Sprite)

```python
>> obj.sprites
[<wmwpy.classes.sprite.Sprite object>]
```

The object image is a `PIL` image.

```python
>> obj.image
<PIL.Image.Image image mode=RGBA size=300x300>
```

The image scale can be set

```python
obj.scale = 20
```

You can also save a GIF of the object animations

```python
obj.saveGIF('broken_pipe.gif')
```

Once you're finished editing the object, you can get the xml.

```python
xml = export('/Objects/broken_pipe.hs',)
```

This returns the xml file as `bytes`, but also saves the file to the game filesystem.

# Building package
To build the package, install `build`
```
pip install build
 ```
 Then run
 ```
py -m build
 ```

# Building docs
 To build the docs, make sure sphinx is installed
 ```
pip install -r doc-build/requirements.txt
 ```

 You then need to run
 ```
sphinx-build -b html doc-build docs
 ```

# Credits
- Thanks to [@campbellsonic](https://github.com/campbellsonic) for the script to read waltex images. I could not have done it without them.
- Thanks to [Mark Setchell](https://stackoverflow.com/a/75511423/17129659) for helping to make loading waltex images faster (still need rgb565 and rgba5551).
