class CollisionSolver:
    """
    Clase estática utilitaria para resolver colisiones matemáticas en 2D.
    Utiliza el método AABB (Axis-Aligned Bounding Box) para cajas no rotadas.
    """

    @staticmethod
    def aabb_check(pos_a, size_a, pos_b, size_b) -> bool:
        """
        Determina si dos cajas rectangulares se intersectan en un plano 2D.
        pos_x: Tupla (x, y) representando el centro o la esquina superior izquierda.
        size_x: Tupla (width, height) representando las dimensiones de la caja.
        """
        ax1, ay1 = pos_a
        ax2, ay2 = pos_a[0] + size_a[0], pos_a[1] + size_a[1]

        bx1, by1 = pos_b
        bx2, by2 = pos_b[0] + size_b[0], pos_b[1] + size_b[1]

        # Si una caja está a la izquierda, derecha, arriba o abajo de la otra, no hay choque.
        if ax2 <= bx1 or ax1 >= bx2:
            return False
        if ay2 <= by1 or ay1 >= by2:
            return False

        return True

    @staticmethod
    def resolve_elastic_collision(velocity_a, mass_a, velocity_b, mass_b):
        """
        (Avanzado) Resuelve el rebote elástico de velocidades entre dos cuerpos circulares/rectangulares.
        Retorna las nuevas velocidades (new_vel_a, new_vel_b).
        """
        # Una aproximación simple de conservación de movimiento
        total_mass = mass_a + mass_b
        if total_mass == 0: return velocity_a, velocity_b

        new_v_a_x = (velocity_a[0] * (mass_a - mass_b) + (2 * mass_b * velocity_b[0])) / total_mass
        new_v_a_y = (velocity_a[1] * (mass_a - mass_b) + (2 * mass_b * velocity_b[1])) / total_mass

        new_v_b_x = (velocity_b[0] * (mass_b - mass_a) + (2 * mass_a * velocity_a[0])) / total_mass
        new_v_b_y = (velocity_b[1] * (mass_b - mass_a) + (2 * mass_a * velocity_a[1])) / total_mass

        return (new_v_a_x, new_v_a_y), (new_v_b_x, new_v_b_y)