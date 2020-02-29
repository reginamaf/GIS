from flask_restful import Resource
from osgeo import gdal, ogr, osr

class VegetationCoverResult(Resource):
    def get(self):
        return {"filename": self.getFileName(),
                "cover": self.calculateVegetationCoverage(),
                "area": self.calculateArea(),
                "centroid" : self.calculateCentroidCoordinates(),
                "local_time": self.getLocalTime()}

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

    def getFileName(self):
        geotransform = self.getGeotransform()
        return geotransform["fileData"].GetDescription()

    def calculateArea(self):
        geotransform = self.getGeotransform()
        area = geotransform["xSize"] * geotransform["xres"] * geotransform["ySize"] * (-geotransform["yres"])
        return area/10**6

    
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
    
    def calculateVegetationCoverage(self):
        geotransform = self.getGeotransform()
        totalPixels = geotransform["xSize"] * geotransform["ySize"]
        fileData = geotransform["fileData"]
        greenBand = fileData.GetRasterBand(2)
        bandPixels = greenBand.XSize * greenBand.YSize
        print(bandPixels)
        print(totalPixels)
        return bandPixels*100/totalPixels

    def getLocalTime(self):
        geotransform = self.getGeotransform();
        time = geotransform["fileData"].GetMetadataItem("TIFFTAG_DATETIME")
        return time
