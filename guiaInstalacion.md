# Installation of VTK and `pyg4ometry` on WSL2 with Ubuntu 22.04

This guide outlines the steps to install and configure VTK and `pyg4ometry` on a WSL2 environment with Ubuntu 22.04.5 LTS, leveraging the native GUI support of WSLg. It has been tested on Windows 11 with WSL2 enabled.

## Prerequisites
- **Operating System**: Windows 11 with WSL2 enabled.
- **Distribution**: Ubuntu 22.04 LTS installed on WSL2 (`wsl --install -d Ubuntu-22.04` if needed).
- **Terminal Access**: Open a WSL2 terminal with Ubuntu 22.04.

---

## Step 1: Update the System and Install Basic Dependencies

1. Update Ubuntu packages:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt dist-upgrade -y
   ```
2. Install build tools and basic dependencies:
   ```bash
   sudo apt install build-essential cmake git python3 python3-pip python3-dev python3-numpy -y
   ```

---

## Step 2: Install and Configure Graphics Libraries (Mesa)

VTK and `pyg4ometry` require OpenGL/GLX support. The default Mesa version in Ubuntu 22.04 is sufficient, but ensure it’s properly installed:

1. Install graphics libraries:
   ```bash
   sudo apt install mesa-utils libgl1-mesa-glx libgl1-mesa-dev libglu1-mesa-dev freeglut3-dev libxt-dev libx11-dev -y
   ```
2. Verify OpenGL support:
   ```bash
   glxinfo | grep "OpenGL version"
   ```
   You should see something like: `OpenGL version string: 4.6 (Compatibility Profile) Mesa 23.x.x`, or `OpenGL version string: 4.1 (Compatibility Profile) Mesa 23.2.1-1ubuntu3.1~22.04.3`.
   If it fails or shows an old version (e.g., Mesa 10.5.4), reinstall Mesa:
     ```bash
     sudo apt purge mesa-utils libgl1-mesa-glx libgl1-mesa-dev libglu1-mesa-dev freeglut3-dev -y
     sudo apt autoremove -y
     sudo apt install mesa-utils libgl1-mesa-glx libgl1-mesa-dev libglu1-mesa-dev freeglut3-dev -y
     ```

---

## Step 3: Configure Graphics Support with WSLg

WSL2 on Ubuntu 22.04 supports GUI natively with WSLg, eliminating the need for an external X server like MobaXterm:

For using WSLg:

1. Update WSL on Windows:
   ```cmd
   wsl --update
   ```
   (Run this in a Windows terminal).
2. Check the `DISPLAY` variable:
    ```bash
    echo $DISPLAY
    ```
    The output should be the followinf `:0`. **If not**, set the `DISPLAY` variable for WSLg:
    ```bash
    export DISPLAY=:0
    ```
3. Test graphics support:
   ```bash
   sudo apt install x11-apps -y
   xclock  # Should open a clock
   glxinfo | grep "OpenGL version"  # Verify OpenGL
   ```
For using MobaXterm:
1. Test graphics support:
   ```bash
   glxinfo
   ```
   If it ends with an error message like this:
   `X Error of failed request:  GLXBadCurrentWindow`, then it should appear in the beginning of the output something like this `direct rendering: No (LIBGL_ALWAYS_INDIRECT set)`. In that case, set that environment variable to 0 as follows:
   ```bash
   export LIBGL_ALWAYS_INDIRECT=0
   ```
   And try again.
   
   You can add this line to your bash so you don't need to write it every time.
   ```bash
   echo 'export LIBGL_ALWAYS_INDIRECT=0' >> ~/.bashrc 
   ```
   Although I don't recommend because, in my experience, some ROOT graphics crash after this change.
---

## Step 4: Build and Install VTK from Source

VTK must be built from source to ensure compatibility with WSL2 and `pyg4ometry`:

1. Download VTK 9.4.1:
   ```bash
   mkdir ~/vtk_build && cd ~/vtk_build
   git clone --branch v9.4.1 --depth 1 https://github.com/Kitware/VTK.git
   mkdir VTK_build && cd VTK_build
   ```
2. Configure the build with CMake:
   ```bash
   cmake -S ../VTK -B . \
         -DCMAKE_BUILD_TYPE=Release \
         -DVTK_BUILD_TESTING=OFF \
         -DVTK_WRAP_PYTHON=ON \
         -DVTK_PYTHON_VERSION=3 \
         -DPython3_EXECUTABLE=$(which python3) \
         -DVTK_USE_X=ON
   ```
   - **Note**: Ignore warnings about `OPENGL_gl_LIBRARY`, `OPENGL_glu_LIBRARY`, or `VTK_OPENGL_HAS_OSMESA` if they appear; they don’t affect the build.
3. Compile and install:
   ```bash
   make -j$(nproc)
   sudo make install
   ```
4. Set `PYTHONPATH` so Python can find VTK. Check first the location of the vtk python distribution you have just compiled. It is usually any of this two paths
    ```bash
    ls -lrth /usr/local/lib/python3.10/site-packages
    # or
    ls -lrth /usr/local/lib/python3.10/site-packages
    ```
    you should see a ``vtk.py`` file and ``vtkmodules`` folder
   ```bash
   export PYTHONPATH=/usr/local/lib/python3.10/site-packages:$PYTHONPATH
   ```
   - Make it permanent by adding to `~/.bashrc`:
     ```bash
     echo 'export PYTHONPATH=/usr/local/lib/python3.10/site-packages:$PYTHONPATH' >> ~/.bashrc
     source ~/.bashrc
     ```
5. Verify VTK:
   ```bash
   python3 -c "import vtk; print(vtk.vtkVersion.GetVTKVersion())"
   ```
   - Should output `9.4.1`.

---

## Step 5: Install `pyg4ometry`

1. Install `pyg4ometry` with `pip`:
   ```bash
   pip3 uninstall pyg4ometry  # Clean up if already installed
   pip3 install pyg4ometry
   ```
2. Install recommended additional dependencies:
   ```bash
   pip3 install numpy matplotlib scipy
   ```

---

## Step 6: Test the Installation

1. Test standalone VTK:
   ```python
   import vtk
   render_window = vtk.vtkRenderWindow()
   render_window.SetSize(400, 400)
   render_window.Render()
   input("Press Enter to close")
   ```
   - Should open an empty window without errors.
2. Test `pyg4ometry` with `vtkVisualizer`:
   ```python
   import pyg4ometry.visualisation as vis
   v = vis.VtkViewer()
   v.view()
   ```
   - Should open a visualization window without a "Segmentation fault".
   If the "Segmentation fault" persists, try importing the vtk module before pyg4ometry:
   ```python
   import vtk
   import pyg4ometry.visualisation as vis
   v = vis.VtkViewer()
   v.view()
   ```
---

## Troubleshooting

- **If `glxinfo` fails or shows an old Mesa version**:
  - Reinstall Mesa (see Step 2) or use a modern PPA:
    ```bash
    sudo add-apt-repository ppa:kisak/kisak-mesa -y
    sudo apt update && sudo apt upgrade -y
    sudo apt install mesa-utils libgl1-mesa-glx libgl1-mesa-dev -y
    ```
- **If VTK doesn’t import**:
  - Check `PYTHONPATH` and ensure no pip-installed VTK version conflicts:
    ```bash
    pip3 uninstall vtk
    ```
- **If `pyg4ometry` gives a "Segmentation fault"**:
  - Ensure no VTK version conflicts and try VTK 9.1.0 if needed (adjust Step 4).

---

## Final Notes
- This setup uses WSLg (`DISPLAY=:0`) for simplicity. If you prefer MobaXterm, install it on Windows, start the X server, and use `export DISPLAY=localhost:10.0` or `127.0.0.1:0.0`.
- The steps assume a clean environment. If the system has prior configurations, clean up old installations first (`pip3 uninstall`, `sudo apt purge`, etc.).
