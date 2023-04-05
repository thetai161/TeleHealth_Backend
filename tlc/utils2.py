import os
from keras.models import Model
from keras.layers import Input, concatenate, Conv2D, MaxPooling2D, Reshape, Dropout
from keras.optimizers import Adam
from keras import backend as K
from keras.optimizers import *
from keras.layers import *
import numpy as np
import pydicom
import os
import matplotlib.pyplot as plt
import cv2 as cv
from glob import glob
import scipy.ndimage
from skimage import morphology
from skimage.morphology import binary_dilation, binary_erosion
import matplotlib.pyplot as plt
import scipy.misc
from glob import glob
from skimage import morphology
from scipy.ndimage.morphology import binary_erosion, binary_dilation, binary_fill_holes
import mcubes
from skimage import morphology
from plotly import __version__
from .models import *
seed = 6


def dice_coef(y_true, y_pred, smooth=1e-7):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersect = K.sum(y_true_f * y_pred_f, axis=-1)
    denom = K.sum(y_true_f + y_pred_f, axis=-1)
    return K.mean((2. * intersect / (denom + smooth)))


def dice_loss(y_true, y_pred):
    return 1 - dice_coef(y_true, y_pred)


def BCDU_net_D3(input_size=(256, 256, 1)):
    N = input_size[0]
    inputs = Input(input_size)
    conv1 = Conv2D(64, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(inputs)
    conv1 = Conv2D(64, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv1)

    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)
    conv2 = Conv2D(128, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(pool1)
    conv2 = Conv2D(128, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)
    conv3 = Conv2D(256, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(pool2)
    conv3 = Conv2D(256, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv3)
    drop3 = Dropout(0.5)(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)
    # D1
    conv4 = Conv2D(512, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(pool3)
    conv4_1 = Conv2D(512, 3, activation='relu', padding='same',
                     kernel_initializer='he_normal')(conv4)
    drop4_1 = Dropout(0.5)(conv4_1)
    # D2
    conv4_2 = Conv2D(512, 3, activation='relu', padding='same',
                     kernel_initializer='he_normal')(drop4_1)
    conv4_2 = Conv2D(512, 3, activation='relu', padding='same',
                     kernel_initializer='he_normal')(conv4_2)
    conv4_2 = Dropout(0.5)(conv4_2)
    # D3
    merge_dense = concatenate([conv4_2, drop4_1], axis=3)
    conv4_3 = Conv2D(512, 3, activation='relu', padding='same',
                     kernel_initializer='he_normal')(merge_dense)
    conv4_3 = Conv2D(512, 3, activation='relu', padding='same',
                     kernel_initializer='he_normal')(conv4_3)
    drop4_3 = Dropout(0.5)(conv4_3)

    up6 = Conv2DTranspose(256, kernel_size=2, strides=2,
                          padding='same', kernel_initializer='he_normal')(drop4_3)
    up6 = BatchNormalization(axis=3)(up6)
    up6 = Activation('relu')(up6)

    x1 = Reshape(target_shape=(1, np.int32(N/4), np.int32(N/4), 256))(drop3)
    x2 = Reshape(target_shape=(1, np.int32(N/4), np.int32(N/4), 256))(up6)
    merge6 = concatenate([x1, x2], axis=1)
    merge6 = ConvLSTM2D(filters=128, kernel_size=(3, 3), padding='same',
                        return_sequences=False, go_backwards=True, kernel_initializer='he_normal')(merge6)

    conv6 = Conv2D(256, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(merge6)
    conv6 = Conv2D(256, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv6)

    up7 = Conv2DTranspose(128, kernel_size=2, strides=2,
                          padding='same', kernel_initializer='he_normal')(conv6)
    up7 = BatchNormalization(axis=3)(up7)
    up7 = Activation('relu')(up7)

    x1 = Reshape(target_shape=(1, np.int32(N/2), np.int32(N/2), 128))(conv2)
    x2 = Reshape(target_shape=(1, np.int32(N/2), np.int32(N/2), 128))(up7)
    merge7 = concatenate([x1, x2], axis=1)
    merge7 = ConvLSTM2D(filters=64, kernel_size=(3, 3), padding='same',
                        return_sequences=False, go_backwards=True, kernel_initializer='he_normal')(merge7)

    conv7 = Conv2D(128, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(merge7)
    conv7 = Conv2D(128, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv7)

    up8 = Conv2DTranspose(64, kernel_size=2, strides=2,
                          padding='same', kernel_initializer='he_normal')(conv7)
    up8 = BatchNormalization(axis=3)(up8)
    up8 = Activation('relu')(up8)

    x1 = Reshape(target_shape=(1, N, N, 64))(conv1)
    x2 = Reshape(target_shape=(1, N, N, 64))(up8)
    merge8 = concatenate([x1, x2], axis=1)
    merge8 = ConvLSTM2D(filters=32, kernel_size=(3, 3), padding='same',
                        return_sequences=False, go_backwards=True, kernel_initializer='he_normal')(merge8)

    conv8 = Conv2D(64, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(merge8)
    conv8 = Conv2D(64, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv8)
    conv8 = Conv2D(2, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv8)
    conv9 = Conv2D(3, 1, activation='softmax')(conv8)

    model = Model(inputs, conv9)
    model.compile(optimizer=Adam(learning_rate=1e-4),
                  loss=[dice_loss], metrics=[dice_coef])
    return model


def BCDU_net_D1(input_size=(256, 256, 1)):
    N = input_size[0]
    inputs = Input(input_size)
    conv1 = Conv2D(64, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(inputs)
    conv1 = Conv2D(64, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv1)

    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)
    conv2 = Conv2D(128, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(pool1)
    conv2 = Conv2D(128, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)
    conv3 = Conv2D(256, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(pool2)
    conv3 = Conv2D(256, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv3)
    drop3 = Dropout(0.5)(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)
    # D1
    conv4 = Conv2D(512, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(pool3)
    conv4_1 = Conv2D(512, 3, activation='relu', padding='same',
                     kernel_initializer='he_normal')(conv4)
    drop4_1 = Dropout(0.5)(conv4_1)

    up6 = Conv2DTranspose(256, kernel_size=2, strides=2,
                          padding='same', kernel_initializer='he_normal')(conv4_1)
    up6 = BatchNormalization(axis=3)(up6)
    up6 = Activation('relu')(up6)

    x1 = Reshape(target_shape=(1, np.int32(N/4), np.int32(N/4), 256))(drop3)
    x2 = Reshape(target_shape=(1, np.int32(N/4), np.int32(N/4), 256))(up6)
    merge6 = concatenate([x1, x2], axis=1)
    merge6 = ConvLSTM2D(filters=128, kernel_size=(3, 3), padding='same',
                        return_sequences=False, go_backwards=True, kernel_initializer='he_normal')(merge6)

    conv6 = Conv2D(256, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(merge6)
    conv6 = Conv2D(256, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv6)

    up7 = Conv2DTranspose(128, kernel_size=2, strides=2,
                          padding='same', kernel_initializer='he_normal')(conv6)
    up7 = BatchNormalization(axis=3)(up7)
    up7 = Activation('relu')(up7)

    x1 = Reshape(target_shape=(1, np.int32(N/2), np.int32(N/2), 128))(conv2)
    x2 = Reshape(target_shape=(1, np.int32(N/2), np.int32(N/2), 128))(up7)
    merge7 = concatenate([x1, x2], axis=1)
    merge7 = ConvLSTM2D(filters=64, kernel_size=(3, 3), padding='same',
                        return_sequences=False, go_backwards=True, kernel_initializer='he_normal')(merge7)

    conv7 = Conv2D(128, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(merge7)
    conv7 = Conv2D(128, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv7)

    up8 = Conv2DTranspose(64, kernel_size=2, strides=2,
                          padding='same', kernel_initializer='he_normal')(conv7)
    up8 = BatchNormalization(axis=3)(up8)
    up8 = Activation('relu')(up8)

    x1 = Reshape(target_shape=(1, N, N, 64))(conv1)
    x2 = Reshape(target_shape=(1, N, N, 64))(up8)
    merge8 = concatenate([x1, x2], axis=1)
    merge8 = ConvLSTM2D(filters=32, kernel_size=(3, 3), padding='same',
                        return_sequences=False, go_backwards=True, kernel_initializer='he_normal')(merge8)

    conv8 = Conv2D(64, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(merge8)
    conv8 = Conv2D(64, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv8)
    conv8 = Conv2D(16, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal')(conv8)
    conv9 = Conv2D(3, 1, activation='softmax')(conv8)

    model = Model(inputs, conv9)
    model.compile(optimizer=Adam(learning_rate=1e-4),
                  loss=[dice_loss], metrics=[dice_coef])
    return model


def rescale_affine(input_affine, voxel_dims=[1, 1, 1], target_center_coords=None):
    """
    This function uses a generic approach to rescaling an affine to arbitrary
    voxel dimensions. It allows for affines with off-diagonal elements by
    decomposing the affine matrix into u,s,v (or rather the numpy equivalents)
    and applying the scaling to the scaling matrix (s).

    Parameters
    ----------
    input_affine : np.array of shape 4,4
        Result of nibabel.nifti1.Nifti1Image.affine
    voxel_dims : list
        Length in mm for x,y, and z dimensions of each voxel.
    target_center_coords: list of float
        3 numbers to specify the translation part of the affine if not using the same as the input_affine.

    Returns
    -------
    target_affine : 4x4matrix
        The resampled image.
    """
    # Initialize target_affine
    target_affine = input_affine.copy()
    # Decompose the image affine to allow scaling
    u, s, v = np.linalg.svd(target_affine[:3, :3], full_matrices=False)

    # Rescale the image to the appropriate voxel dimensions
    s = voxel_dims

    # Reconstruct the affine
    target_affine[:3, :3] = u @ np.diag(s) @ v

    # Set the translation component of the affine computed from the input
    # image affine if coordinates are specified by the user.
    if target_center_coords is not None:
        target_affine[:3, 3] = target_center_coords
    return target_affine


def load_scan(path):
    # os.listdir(path) = name of all files in path
    # dicom_read_file() get the dataset of ct image in string type
    slices = [pydicom.read_file(path + '/' + s) for s in os.listdir(path)]
    # order the list by the increasement of instancenumber
    # [(0020,0013),(0020,0011),(0020,0015)]->[(0020,0011),(0020,0013),(0020,0015)]
    slices.sort(key=lambda x: int(x.InstanceNumber))
    # if 'try' fail or error, 'except' code will be operated
    try:
        slice_thickness = np.abs(
            slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(
            slices[0].SliceLocation - slices[1].SliceLocation)
    for s in slices:
        s.SliceThickness = slice_thickness
    return slices

# convert raw values of voxel in the images to HU


def get_pixels_hu(scans):
    # s.pixel_array get ct image's pixel data in matrix
    # np.stack join many array(matrix) with the same dimension into new sequence
    image = np.stack([s.pixel_array for s in scans])
    # should be possible as values should always be low enough (<32k)
    # convert all dataframe columns into dtype int16
    image = image.astype(np.int16)
    # Set outside-of-scan pixels (HU = -2000) to 0
    # The intercept(threshold) is usually -1024, so air is approximately 0
    image[image == -2000] = 0
    # Convert to Hounsfield units (HU=pixel_value*slope+intercept)
    intercept = scans[0].RescaleIntercept
    slope = scans[0].RescaleSlope
    if slope != 1:
        image = slope * image.astype(np.float64)
        image = image.astype(np.int16)
    image += np.int16(intercept)
    return np.array(image, dtype=np.int16)


def resample(image, scan, new_spacing=[1, 1, 1]):
    # Determine current pixel spacing
    # map(function,iterable) -> return a list,tuple to inform function
    # get scan to be in form of float number
    spacing = [scan[0].SliceThickness,
               scan[0].PixelSpacing[0], scan[0].PixelSpacing[1]]
    # change list to array
    spacing = np.array(spacing)

    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    new_spacing = spacing / real_resize_factor
    image = scipy.ndimage.interpolation.zoom(image, real_resize_factor)

    return image, new_spacing


def hu_to_grayscale(volume):
    volume = np.clip(volume, -512, 512)
    mxval = np.max(volume)
    mnval = np.min(volume)
    im_volume = (volume - mnval)/max(mxval - mnval, 1e-3)
    im_volume = im_volume
    return im_volume * 255


def get_mask_alung(vol):
    vol_im = np.where(vol > 0, 1, 0).astype('bool')
    shp = vol.shape
    around_lung = np.zeros((shp[0], shp[1], shp[2]), dtype='bool')
    for idx in range(shp[0]):
        # around_lung[idx, :, :] = binary_dilation(vol_im[idx], structure=np.ones((3,3))).astype(vol_im.dtype)
        around_lung[idx, :, :] = binary_erosion(
            vol_im[idx], structure=np.ones((2, 2))).astype(vol_im.dtype)
        around_lung[idx, :, :] = binary_fill_holes(
            around_lung[idx, :, :], structure=np.ones((6, 6))).astype(vol_im.dtype)
        around_lung[idx, :, :] = binary_erosion(
            around_lung[idx, :, :], structure=np.ones((7, 7))).astype(vol_im.dtype)
        around_lung[idx, :, :] = morphology.remove_small_objects(
            around_lung[idx, :, :], min_size=750)
        around_lung[idx, :, :] = binary_dilation(
            around_lung[idx, :, :], structure=np.ones((10, 10))).astype(vol_im.dtype)
    return around_lung


def get_data(vol):
    vol_ims = hu_to_grayscale(vol)
    around_lung = get_mask_alung(vol_ims).astype(vol_ims.dtype)
    vol_after = np.multiply(vol_ims, around_lung)
    return vol_after


def load_data(url, user, urlk):
    data_path = url
    # export result to other folder
    output_path = working_path = './media'
    # open dicom files
    g = glob(data_path+'/*.dcm')
    patient = load_scan(data_path)
    print("slice thickness: %f" % patient[0].SliceThickness)
    r = patient[0].PixelSpacing[0]
    c = patient[0].PixelSpacing[1]
    # print("pixel spacing (row,col): (%f, %f)" %(patient[0].PixelSpacing[0], patient[0].PixelSpacing[1]))
    print(r)
    print(c)
    imgs = get_pixels_hu(patient)
    # save an array to a numpy file (.npy) format
    # np.save(output_path + "fullimages_%d.npy" %(id), imgs)
    # file_used=output_path+"fullimages_%d.npy" % id

    # imgs_to_process = np.load(file_used).astype(np.float64)
    imgs_to_process = imgs.astype(np.float32)

    imgs_after_resamp, spacing = resample(
        imgs_to_process, patient, [1, r*1.99, c*1.99])
    imgs_after_resamp = imgs_after_resamp[:, :256, :256]
    new_size = imgs_after_resamp.shape
    print('image orginal:', imgs_to_process.shape)
    print('image after resamp:', imgs_after_resamp.shape)
    print('voxel value:', spacing)
    vol = get_data(imgs_after_resamp)
    vol = np.moveaxis(vol, 1, 2)
    data = []
    for idx in range(vol.shape[0]):
        data.append(vol[idx, :, :])
    data = np.array(data).astype('float32')
    # data = np.flip(data)
    tr_data = np.expand_dims(data, axis=3)
    tr_data = tr_data/255.
    model = BCDU_net_D3(input_size=(256, 256, 1))
    model.load_weights('./tlc/BCDU_net')
    predictions = model.predict(tr_data, batch_size=2, verbose=1)
    mask = np.argmax(predictions, axis=3)
    right = 0
    left = 0
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            for k in range(mask.shape[2]):
                if mask[i][j][k] == 1:
                    right += 1
                if mask[i][j][k] == 2:
                    left += 1
    vol_r = int(right * spacing[0] * spacing[1] * spacing[2] / 1000)
    vol_l = int(left * spacing[0] * spacing[1] * spacing[2] / 1000)
    volume = vol_r+vol_l
    print('Right Lung Volume:', vol_r, 'ml')
    print('Left Lung Volume:', vol_l, 'ml')
    print('Total Lung Capacity:', volume, 'ml')
    UserFile = UserUploadedFile.objects.create(patient_id=user, drive_id=0)
    UserFile.save()
    Result = ResultFile.objects.create(upload_file=UserFile, right_lung=vol_r, left_lung=vol_l,
                                       lung_volume=volume, url=urlk)
    Result.save()
    mask = np.flip(mask)
    p = mask.transpose(2, 1, 0)
    smoothed_sphere = mcubes.smooth(p, method='gaussian', sigma=1.25)
    verts, faces = mcubes.marching_cubes(smoothed_sphere, 0)
    z = verts[faces]
    return vol_r, vol_l, volume, z
