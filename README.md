# LVSoftware
This is a repository for useful Software developed by utilising sav files

# ColourChanger_V3_Free
```
## Description: 
```
This is a program for changing Hair, Skin Colour 

The main purpose of this program is changing it without 'manually hard coding in characterStyle-1.0.sav files'

The system will automatically change it by showing handy GUI and also RGB selector
```

## How to use:
```
1) Set the path of directory of SaveGames DIR having all sav files
(Normally C:\Users\PC\AppData\Local\Longvinter\Saved\SaveGames)

2) Select the colour you want in each parts
(If you leave some parts like before, just leave it)

3) If you want to make your hair like actual Bald, turn the "BALDY MODE" ON

4) If you done, click the 'save' button for saving all changes
```
## How it works:
```
1) It reads sav file (characterStyle-1.0.sav) via 'uesave' --> UE sav reader

2) get data and make json files for it
 
3) GET string for data from json file 
 
4) change some values in it

5) via using uesave again, save this string into .sav file
```
```
