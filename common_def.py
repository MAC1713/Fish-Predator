def limit_vector(vector, max_magnitude):
    if vector.length() > max_magnitude:
        return vector.normalize() * max_magnitude
    return vector
