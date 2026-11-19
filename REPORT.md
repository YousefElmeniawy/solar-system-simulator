# Interactive 3D Solar System Simulator

**Course:** IT311 — Computer Graphics  
**Implementation:** Python 3, Pygame, PyOpenGL and GLSL 3.3 Core

## Abstract

This project implements an interactive three-dimensional solar-system visualization as an educational demonstration of the graphics pipeline, homogeneous transformations, hierarchical modeling, camera projection, lighting, real-time animation and particle systems. The system renders the Sun, eight planets, the Moon, Saturn's rings, sampled orbit curves, a procedural star field and solar-wind particles. It has no Mission Control side panel or Earth magnetic-field mode. All mesh generation, camera mathematics, transformations and animation logic are explicit and organized into modules. The system is designed for demonstration and explanation; its visual scale and scientific data are intentionally approximate.

## 1. Introduction

A solar-system simulator is a useful setting for bringing together geometric modeling, transformations, visibility, shading and time-based motion. The challenge is to display a large range of planetary sizes and distances while retaining readable visual relationships and responsive interaction. This implementation prioritizes clear graphics concepts and stable, explainable algorithms over astronomical scale accuracy.

## 2. Problem statement

A static illustration cannot demonstrate how hierarchical transforms, camera matrices, shading, projections and animation work together. The project addresses this by producing a running scene in which the viewer can select bodies, move the camera, switch projection modes, pause and accelerate time, and independently toggle visual layers.

## 3. Objectives

1. Implement a shader-driven 3D scene in Python and OpenGL without a game engine.
2. Provide explicit vector and 4×4 matrix operations, including `look_at`, perspective and orthographic projections.
3. Demonstrate parent-child transforms for the Earth–Moon system and Saturn's rings.
4. Animate orbital and axial rotation from elapsed time rather than frame count.
5. Demonstrate Phong-family lighting, depth testing, face culling, parametric curves and a particle system.
6. Provide a usable camera, planet selection, compact HUD and keyboard/mouse controls.
7. Document assumptions and validate core calculations with automated tests.

## 4. Design and architecture

`main.py` launches `src.app`. The app owns the Pygame window, event loop and simulation state. `scene.py` calculates world transforms. `math3d.py` supplies the explicitly implemented matrix routines. `mesh.py` produces immutable procedural sphere, ring and orbit vertex data. `renderer.py` uploads static geometry to VAOs/VBOs, compiles shaders and renders the scene. `camera.py` manages orbit-camera state and projections. `animation.py` advances simulation time; `particles.py` updates solar-wind samples. `ui.py` draws a compact status HUD and optional keyboard-help overlay on a transparent Pygame surface, which is composited as a texture in the OpenGL context. The Mission Control side panel was removed. Planet facts are stored in `planet_data.py` rather than scattered through rendering code.

## 5. Mathematical model

### 5.1 Homogeneous transformations

A point `(x,y,z)` is extended to `(x,y,z,1)` and a direction to `(x,y,z,0)`. The module implements identity, translation, scaling, rotations about X/Y/Z, multiplication, normalization, dot and cross products, and point/vector transforms. Composition uses column-vector semantics; for a vertex `p`, the pipeline is `p_clip = P V M p_local`.

### 5.2 Camera and projections

The view matrix is derived from `forward = normalize(target − eye)`, `right = normalize(forward × up)`, and a corrected up vector. Its rows form the camera basis and include translated dot products. The perspective matrix uses the field of view and aspect ratio, while orthographic projection maps a specified cuboid directly to clip space. Degenerate projection parameters are rejected. The orbit camera clamps zoom and pitch to avoid singularities and unreasonable distances.

### 5.3 Orbital and spin motion

For a planet with orbital period `T` (Earth days), the orbital phase is `theta(t)=theta0+2πt/T`. A slightly eccentric parametric orbit is sampled for trails; the displayed body location uses its corresponding ellipse radius and phase. Axial rotation is computed from elapsed simulation time and the approximate spin period. A rate multiplier changes simulated days per real second. The clock clamps unusually large frame gaps to avoid jumps after a pause or debugger stop.

### 5.4 Hierarchical transforms

The Moon's transform is `M_Earth × T_orbit × R_lunar × S_moon`, with the Earth's complete world transform applied first. As a result, the Moon remains around Earth as Earth travels around the Sun. Saturn's ring mesh is a child at Saturn's translated, tilted frame and has its own annular geometry. These matrix products make parent-child relationships inspectable in the source.

### 5.5 Particle integration

Solar-wind particles maintain position, velocity, color, lifetime and a maximum lifetime. Each update applies a weak radial acceleration and then advances velocity and position using semi-implicit Euler integration. Particles that expire or leave the scene are respawned. A fixed seeded random generator makes initial conditions reproducible.

## 6. Rendering pipeline

1. CPU scene code produces each body's model matrix.
2. Static local-space positions are read from vertex buffers.
3. The vertex shader transforms vertices by `Projection × View × Model` and transforms normals using the inverse-transpose model matrix.
4. The fragment shader computes ambient, Lambert diffuse and Blinn–Phong specular contributions; the Sun is emissive.
5. The depth buffer resolves visibility; back-face culling removes hidden sphere surfaces. Ring faces are rendered two-sided.
6. OpenGL clips and divides to normalized device coordinates and maps them to the viewport.
7. A transparent Pygame HUD texture is blended over the completed 3D image.

The star field and sphere/orbit/ring geometry are generated once and held in GPU buffers. The particle VBO is updated as a dynamic buffer each frame. Planet and star textures are not required; procedural geometry and per-body materials provide deterministic visual fallback without external assets.

## 7. Implementation details

The renderer requests an OpenGL 3.3 Core context and compiles shaders from the local `shaders/` directory. Error messages report unavailable contexts or shader compilation failures. The application requires Python 3.10+, Pygame, NumPy, PyOpenGL and a graphics implementation supporting OpenGL 3.3 Core. A modern software Mesa context may be usable on systems without a dedicated GPU. The code does not include a pre-3.3 renderer fallback.

Planet radius and orbit distance are adjusted for legibility. The Sun is a luminous central point source; ambient illumination prevents the unlit hemisphere from disappearing entirely. Selection highlights a body and labels can be toggled. There is no Mission Control or planet-information side panel; body selection, labels and focus remain available through the scene and keyboard.

## 8. Interaction design

The Mission Control side panel and Earth magnetic-field feature have been removed. The compact HUD presents simulation day, pause state, speed, FPS, projection type and camera position. Direct keyboard and mouse controls are listed in `README.md`; a help overlay is available with `?`. The scene supports click selection and mouse-drag orbit, while the camera can focus a selected world or return to a full-system view.

## 9. Results and validation

The CPU-side automated test suite checks identity and translation matrices, rotation and matrix composition, vector normalization and cross products, camera orientation, projection matrices, planet records, time/speed/pause behavior, orbital movement and parent-child Moon composition. Run it with `python -m unittest discover -s tests -v` from the project directory.

A graphical smoke test was performed using an OpenGL Core context on Mesa llvmpipe. The window, shaders, solar-system scene, compact HUD and keyboard-driven application loop were exercised; the automated test suite validates the CPU-side math and simulation logic.

## 10. Limitations

- Visual radii and orbital distances are compressed and exaggerated; the scene is not to scale.
- Orbital/spin periods, temperatures and moon totals are rounded reference values and are not an ephemeris.
- The project uses simple procedural materials rather than image textures; surface detail such as continents and cloud systems is not represented.
- The optional VR/stereo preview is not implemented.
- A compatibility renderer for OpenGL versions below 3.3 is not bundled.

## 11. Future work

Future extensions could add licensed planetary textures, eccentric and inclined orbits using a more complete orbital-element model, picking from an ID buffer, stereo rendering, localization, and performance benchmarks across GPUs. Each extension should preserve the visible relationship between source mathematics and rendered output.

## 12. Conclusion

The simulator brings core IT311 topics together in a modular, inspectable application. Its central educational value lies in explicit transformations, hierarchical models, camera projections, GPU shaders, time-based updates and interactive visualization layers rather than a claim of physically exact scale.

## References

1. NASA Solar System Exploration, Planets: <https://solarsystem.nasa.gov/planets/overview/>.
2. NASA/NSSDC, Planetary Fact Sheet: <https://nssdc.gsfc.nasa.gov/planetary/factsheet/>.
3. NASA Science, Solar System: <https://science.nasa.gov/solar-system/>.

Rounded planet facts are organized in `src/planet_data.py` and should be cross-checked against the above public references if used in a formal submission.
