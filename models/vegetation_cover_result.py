from flask_restful import Resource
from osgeo import gdal, ogr, osr
import numpy as np
import ntpath

class VegetationCoverResult(Resource):
    def get(self):
        try:
            data = {"filename": self.getFileName(),
                    "cover": self.calculateVegetationCoverage(),
                    "area": self.calculateArea(),
                    "centroid" : self.calculateCentroidCoordinates(),
                    "local_time": self.getLocalTime()}
            return data, 200

        except:
            return "Could'nt execute coverage calculations.", 400

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
        path = geotransform["fileData"].GetDescription()
        return ntpath.basename(path)

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
        fileData = geotransform["fileData"]
        redBand = fileData.GetRasterBand(3)
        nirBand = fileData.GetRasterBand(4)
        red = redBand.ReadAsArray().astype(np.float)
        nir = nirBand.ReadAsArray().astype(np.float)
        np.seterr(divide='ignore', invalid='ignore')
        check = np.logical_or ( red > 0, nir > 0 )
        ndvi = np.where (check,  (nir - red ) / ( nir + red ), -999)
        totalSize = ndvi.size
        # NDVI bigger than zero represents vegetation
        biggerThanZero = np.count_nonzero(ndvi > 0)
        vCover = biggerThanZero*100/totalSize
        return vCover

    def getLocalTime(self):
        geotransform = self.getGeotransform()
        time = geotransform["fileData"].GetMetadataItem("TIFFTAG_DATETIME")
        if time is None:
            return "No Date and Time information found in file" 
        else:
            return time
