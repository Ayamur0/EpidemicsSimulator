import math


class CircleGrid:
    def _estimate_points(radius: int):
        return radius * radius * math.pi

    def _estimate_points_3D(radius: int):
        return radius * radius * math.pi * 4

    def _calculate_points(radius: int):
        points = []
        for x in range(-radius, radius + 1):
            Y = int((radius * radius - x * x) ** 0.5)
            for y in range(-Y, Y + 1):
                points.append([x, y])
        return points

    def _calculate_points_3D(radius: int):
        points = []
        for f in range(-radius, radius + 1):
            z = int((radius * radius - f * f) ** 0.5)
            for x in range(-z, z + 1):
                Y = int(((z) * (z) - x * x) ** 0.5)
                for y in range(-Y, Y + 1):
                    points.append([x, y, f])
        return points

    def get_points(amount: int):
        radius = -1
        for i in range(0, 100):
            if CircleGrid._estimate_points(i) >= amount:
                radius = i - 1
                break
        while len(points := CircleGrid._calculate_points(radius)) < amount:
            radius += 1
            points = CircleGrid._calculate_points(radius)
        return points[:amount]

    def get_points_3D(amount: int):
        radius = -1
        for i in range(0, 100):
            if CircleGrid._estimate_points_3D(i) >= amount:
                radius = i - 1
                break
        while len(points := CircleGrid._calculate_points_3D(radius)) < amount:
            radius += 1
        return points[:amount]

    def calculate_radius_3D(amount: int):
        radius = -1
        for i in range(0, 100):
            if CircleGrid._estimate_points_3D(i) >= amount:
                radius = i - 1
                break
        while len(points := CircleGrid._calculate_points_3D(radius)) < amount:
            radius += 1
        return radius
