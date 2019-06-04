def intersect(l1x1, l1y1, l1x2, l1y2, l2x1, l2y1, l2x2, l2y2):
    u1t = (l2x2 - l2x1) * (l1y1 - l2y1) - (l2y2 - l2y1) * (l1x1 - l2x1)
    u2t = (l1x2 - l1x1) * (l1y1 - l2y1) - (l1y2 - l1y1) * (l1x1 - l2x1)
    u2  = (l2y2 - l2y1) * (l1x2 - l1x1) - (l2x2 - l2x1) * (l1y2 - l1y1)

    if u2 != 0:
        u1 = u1t / u2
        u02 = u2t / u2

        if 0 <= u1:
            if u1 <= 1:
                if 0 <= u02:
                    if u02 <= 1:
                        return True
        return False

    else:
        if u1t == 0:
            return True

        if u2t == 0:
            return True

        return False
