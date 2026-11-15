
# The clarke wright algorithm calculates how much distance is saved by joining 2 separate routes.
# The algorithm picks the routes with the most distance savings and tries to combine them.
# If the algorithm can merge routes it will continue to do so until no more distance savings are possible.
# Input needed for algorithm: Distance matrix of all hubs and hub numbers that correlate to distance matrix indices.
# Returns a list of hub numbers. list is in order of efficient route path.
def clarke_wright(distance_matrix, hubs_to_visit):
    # Start with each required hub in its own route from depot->hub->depot
    routes = [[0, hub, 0] for hub in hubs_to_visit]

    # Calculate savings list using the actual hub numbers
    savings = [
        (distance_matrix[0][i] + distance_matrix[0][j] - distance_matrix[i][j], i, j)
        for i in hubs_to_visit
        for j in hubs_to_visit
        if i < j
    ]
    savings.sort(key=lambda s: s[0], reverse=True)

    # Find a route given a specific hub node
    def find_route(node):
        return next(r for r in routes if node in r)

    for _, i, j in savings:
        route_i = find_route(i)
        route_j = find_route(j)

        # Skip if already in the same route
        if route_i is route_j:
            continue

        # Possible merge cases
        if i == route_i[-2] and j == route_j[1]:
            merged = route_i[:-1] + route_j[1:]
        elif j == route_i[-2] and i == route_j[1]:
            merged = route_i[:-1] + route_j[1:]
        elif i == route_i[1] and j == route_j[-2]:
            merged = route_i[::-1][:-1] + route_j[1:]
        elif j == route_i[1] and i == route_j[-2]:
            merged = route_i[:-1] + route_j[::-1][1:]
        else:
            continue  # No valid merge

        routes.remove(route_i)
        routes.remove(route_j)
        routes.append(merged)
    return routes[0]
