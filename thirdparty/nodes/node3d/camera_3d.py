from thirdparty.nodes.node3d.node3d import Node3D, Vector3

class Camera3D(Node3D):
    """
    Representa el punto de vista del jugador en un entorno 3D.
    Contiene la lógica matemática para proyectar objetos tridimensionales a la pantalla 2D.
    """

    def __init__(self, name: str = "Camera3D"):
        super().__init__(name)
        
        self.fov: float = 70.0          # Campo de visión (Field of View) en grados
        self.near_clip: float = 0.1     # Distancia mínima de renderizado
        self.far_clip: float = 1000.0   # Distancia máxima de renderizado
        self.aspect_ratio: float = 16.0 / 9.0

        self.is_current: bool = True     # Si esta cámara está activa

    def project_point(self, world_point: Vector3) -> Tuple[float, float]:
        """
        Matemática de Proyección de Perspectiva simple.
        Pasa un punto tridimensional (X,Y,Z) a coordenadas de pantalla bidimensionales (X,Y).
        """
        cam_pos = self.get_global_position()
        
        # Traslación relativa a la cámara
        rel_x = world_point.x - cam_pos.x
        rel_y = world_point.y - cam_pos.y
        rel_z = world_point.z - cam_pos.z

        # Evitar división por cero (detrás de la cámara)
        if rel_z <= self.near_clip:
            return (-1.0, -1.0) # Fuera de pantalla

        # Fórmulas de proyección de perspectiva básicas: x' = x / z, y' = y / z
        # Se escala por el FOV para simular zoom óptico
        focal_length = 1.0 / (rel_z * math.tan(math.radians(self.fov / 2)))
        
        screen_x = rel_x * focal_length * self.aspect_ratio
        screen_y = rel_y * focal_length

        return (screen_x, screen_y)