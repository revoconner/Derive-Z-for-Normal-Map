# Derive Z for Normal Maps
A simple Windows program to derive blue (Z) channel for normal maps with only Red and Green channels.

## Why is it needed? 
Most game engines will ignore the blue channel of a normal map and derive it during runtime, to save memory. So many artists will use that third channel (blue) to pack other textures data. It works fine in the engine, but if you need to export it and use that texture in a DCC program it may not work as expected without the correct blue channel. 

This app let's you reconstruct the Blue channel from the existing Red and Green channel and allow you to save the reconstructed normal map with all three channels intact.

## How to use

![image](https://github.com/user-attachments/assets/9c87af7a-a0ef-47db-8b9d-c3a6c65e87af)

1. Download (from the releases) and run the **Derive Z for Normal Maps.exe**
2. Select an image file using the "browse" button. You will see a preview on the left side if the image is supported.
3. Click the "Process" button to reconstruct the normal map. You will see a preivew on the right side if things go okay.
4. Click "Save As" button to save the image as jpg, png or tga with the filename and location you want.


## Supported formats
1. Jpeg
2. png
3. tga (targa)

## Changelog
v1.0 - Initial commit
