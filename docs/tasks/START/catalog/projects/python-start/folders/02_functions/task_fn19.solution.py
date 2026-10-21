def task_fn19_taxi_fare(km, is_night):
    fare = 100 + 30 * km
    if is_night:
        fare = fare * 2
    if fare < 150:
        fare = 150
    return fare
