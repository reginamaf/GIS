from flask_restful import Resource
from osgeo import gdal, ogr, osr

class VegetationCoverResult(Resource):
    def get(self):
        return {"filename": "name",
                "cover": "coverage",
                "area": "areaRange",
                "centroid" : self.calculateCentroidCoordinates(),
                "local_time": "time"}

    def getGeotransform(self):
        fileData = gdal.Open('./models/analytic.tif', gdal.GA_ReadOnly)
        ULX_INDEX = 0
        ULY_INDEX = 3
        XRES_INDEX = 1
        YRES_INDEX = 5
        # ulx, uly: upper left point coordinates
        # lrx, lry: lower right point coordinates
        # xres, yres: resolution of pixels
        geotransform = fileData.GetGeoTransform()
        xres = geotransform[XRES_INDEX]
        yres = geotransform[YRES_INDEX]
        ulx = geotransform[ULX_INDEX]
        uly = geotransform[ULY_INDEX]
        lrx = ulx + (fileData.RasterXSize * xres)
        lry = uly + (fileData.RasterYSize * yres)
        return dict (
            xres = xres,
            yres = yres,
            ulx = ulx,
            uly = uly,
            lrx = lrx,
            lry = lry,
            xSize = fileData.RasterXSize,
            ySize = fileData.RasterYSize,
            fileData = fileData
        )

    def calculateArea(self):
        return {}

    
    def calculateCentroidCoordinates(self):
            geotransform = self.getGeotransform()
            ulx = geotransform["ulx"]
            uly = geotransform["uly"]
            xres = geotransform["xres"]
            yres = geotransform["yres"]
            lrx = ulx + (geotransform["xSize"] * xres)
            lry = uly + (geotransform["ySize"] * yres)
            # Calculate coordinates of centroid
            cx = (lrx - ulx)/2 + ulx
            cy = (lry - uly)/2 + uly
            # Transform coordinates of centroid
            source = osr.SpatialReference()
            source.ImportFromWkt(geotransform["fileData"].GetProjection())
            target = osr.SpatialReference()
            target.ImportFromEPSG(4326)
            transform = osr.CoordinateTransformation(source, target)
            transform.TransformPoint(cx, cy)
            return {
                "x": cx,
                "y": cy
            }


