import math
import unittest
import numpy as np
from src.math3d import (identity, translation, scaling, rotation_y, multiply, transform_point,
                        transform_vector, cross, normalize, look_at, perspective, orthographic)
from src.planet_data import PLANETS, BY_KEY
from src.animation import SimulationClock
from src.scene import SolarScene
from src.camera import OrbitCamera
from src.particles import SolarWind

class Math3DTests(unittest.TestCase):
    def test_identity(self): np.testing.assert_allclose(identity(),np.eye(4))
    def test_translation_point_and_vector(self):
        m=translation(2,-3,4)
        np.testing.assert_allclose(transform_point(m,np.array([1,2,3])),[3,-1,7])
        np.testing.assert_allclose(transform_vector(m,np.array([1,2,3])),[1,2,3])
    def test_rotation_y_quarter_turn(self): np.testing.assert_allclose(transform_point(rotation_y(math.pi/2),np.array([1,0,0])),[0,0,-1],atol=1e-7)
    def test_composite_multiply_order(self):
        m=multiply(translation(4,0,0),scaling(2))
        np.testing.assert_allclose(transform_point(m,np.array([1,0,0])),[6,0,0])
    def test_cross_and_normalization(self):
        np.testing.assert_allclose(cross(np.array([1,0,0]),np.array([0,1,0])),[0,0,1])
        np.testing.assert_allclose(normalize(np.array([0,3,4])),[0,.6,.8])
    def test_look_at_camera_points_forward(self):
        v=look_at(np.array([0,0,5]),np.array([0,0,0]),np.array([0,1,0]))
        p=v@np.array([0,0,0,1]); self.assertAlmostEqual(p[2],-5)
        vertical=look_at(np.array([0,0,0]),np.array([0,1,0]),np.array([0,1,0]))
        self.assertTrue(np.isfinite(vertical).all())
    def test_projections(self):
        p=perspective(60,16/9,.1,100); self.assertEqual(p.shape,(4,4)); self.assertAlmostEqual(p[3,2],-1)
        o=orthographic(-2,2,-1,1,.1,10); self.assertAlmostEqual(o[0,0],.5)
        with self.assertRaises(ValueError): perspective(180,1,.1,100)

class ProjectDataAndSimulationTests(unittest.TestCase):
    def test_all_eight_planets_have_complete_data(self):
        self.assertEqual(len(PLANETS),8)
        self.assertEqual(set(BY_KEY),{'mercury','venus','earth','mars','jupiter','saturn','uranus','neptune'})
        for p in PLANETS: self.assertGreater(p.radius,0); self.assertGreater(p.orbit_radius,0); self.assertTrue(p.detail)
    def test_clock_delta_speed_pause_and_reset(self):
        c=SimulationClock(days_per_second=10); c.update(.5); self.assertAlmostEqual(c.days,1.0) # dt capped at .1
        c.change_speed(1); c.update(.1); self.assertAlmostEqual(c.days,11.0)
        c.toggle_pause(); c.update(1.0); self.assertAlmostEqual(c.days,11.0)
        c.reset(); self.assertEqual(c.days,0)
    def test_scene_contains_hierarchical_moon_and_saturn_rings(self):
        scene=SolarScene(); bodies=scene.bodies(15,'earth'); keys={b.key for b in bodies}
        self.assertTrue({'earth','moon','saturn_rings'}.issubset(keys))
        earth=next(b for b in bodies if b.key=='earth'); moon=next(b for b in bodies if b.key=='moon')
        self.assertNotEqual(earth.world_position,moon.world_position)
        np.testing.assert_allclose(moon.model,scene.moon_model)
    def test_orbit_positions_advance_over_time(self):
        scene=SolarScene(); scene.bodies(0); first=scene.planet_positions['earth'].copy()
        scene.bodies(90); second=scene.planet_positions['earth'].copy()
        self.assertGreater(float(np.linalg.norm(first-second)),.01)
    def test_camera_projection_switch_and_zoom_limits(self):
        camera=OrbitCamera(); perspective_matrix=camera.projection_matrix(1280,800)
        camera.orthographic_mode=True; orthographic_matrix=camera.projection_matrix(1280,800)
        self.assertFalse(np.allclose(perspective_matrix,orthographic_matrix))
        camera.zoom(1000); self.assertGreaterEqual(camera.ortho_scale,3.5)
        camera.zoom(-1000); self.assertLessEqual(camera.ortho_scale,120.0)
    def test_particle_integration_changes_positions_and_stays_finite(self):
        system=SolarWind(count=24,seed=5); before=system.positions.copy()
        system.update(.04,1.0)
        self.assertFalse(np.allclose(before,system.positions))
        positions,colors,alpha,sizes=system.drawable()
        self.assertEqual(positions.shape,(24,3)); self.assertTrue(np.isfinite(positions).all())
        self.assertTrue(np.all((alpha>=0)&(alpha<=1))); self.assertTrue(np.all(sizes>0))

if __name__=='__main__': unittest.main(verbosity=2)
