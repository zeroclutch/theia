X_COORD = 0
Y_COORD = 1
 

class ContinuousCorrection:
    corners = [
        [[0,0],[1,0]],
        [[0,1],[1,1]]
    ]

    enabled = False

    def __init__(self, type):
        self.enabled = type == 'geometric'

    # adds a point to the correction matrix.
    # (x1, y1) -> wrong point, (x2, y2) -> right point
    def add(self, x1, y1, x2, y2):
        if self.enabled is False:
            return False
        
        xmean = (x1+x2)/2
        ymean = (y1+y2)/2

        dx = x1-x2
        dy = y1-y2

        for y in range(0, 2):
            for x in range(0, 2):
                self.corners[y][x][X_COORD] += (x - xmean) * dx
                self.corners[y][x][Y_COORD] += (y - ymean) * dy
        
        print('Added from ({0}, {1}) to ({2},{3})'.format(x1,y1,x2,y2))
        print('Corners now at {0}'.format(self.corners))
    
    # map x,y coordinate pair to corrected coordinates
    def map(self,x,y):
        if self.enabled is False:
            return (x,y)
        top_corner = self.corners[0][0]
        bottom_corner = self.corners[1][1]

        width  = bottom_corner[X_COORD] - top_corner[X_COORD] 
        height = bottom_corner[Y_COORD] - top_corner[Y_COORD]

        x0 = width * x + top_corner[X_COORD]
        y0 = height * y + top_corner[Y_COORD]
        # print('Correction from ({0}, {1}) to ({2},{3})'.format(x,y,x0,y0))
        return (x0, y0)
        


if __name__ == "__main__":
    cc = ContinuousCorrection()

    cc.add(0.1, 0.1, 0.2, 0.2)
    cc.add(0.3, 0.1, 0.2, 0.2)
    cc.add(0.1, 0.3, 0.2, 0.2)
    cc.add(0.2, 0.2, 0.2, 0.2)
    cc.add(0.1, 0.2, 0.2, 0.2)
    print(cc.map(0.5, 0.5))
    print(cc.corners)
