/**
 * @file imdiff.c
 * @brief Image difference calculator program
 * @author Pascal Getreuer <getreuer@gmail.com>
 *
 * This file implements the imdiff program, a command line tool for comparing
 * two images with various image quality metrics.  The possible metrics are
 *    - Maximum absolute difference, max_n |A_n - B_n|
 *    - Mean squared error, 1/N sum |A_n - B_n|^2
 *    - Root mean squared error, (MSE)^1/2
 *    - Peak signal-to-noise ratio, -10 log10(MSE/255^2)
 *    - Mean structural similarity index (MSSIM)
 * where N is the number of pixels and subscript n denotes the nth pixel.
 * 
 * The program can also create a difference image, computed as
 *    D_n = 255/2 ((A_n - B_n)/D + 1)
 * where values outside of the range [0,255] are saturated.
 * 
 * Image alpha channels are ignored.  Also beware that although the program can
 * read 16-bit PNG images (provided LIBPNG_SUPPORT is enabled), the image data 
 * is quantized internally to 8 bits.
 * 
 * 
 * Copyright (c) 2010-2011, Pascal Getreuer
 * All rights reserved.
 * 
 * This program is free software: you can use, modify and/or 
 * redistribute it under the terms of the simplified BSD License. You 
 * should have received a copy of this license along this program. If 
 * not, see <http://www.opensource.org/licenses/bsd-license.html>.
 */

#include <math.h>
#include <string.h>
#include <ctype.h>

#include "imageio.h"
#include "conv.h"


/** @brief Display metrics for intensities in the range [0,DISPLAY_SCALING] */
#define DISPLAY_SCALING     255

#define MSSIM_K1            0.01
#define MSSIM_K2            0.03

#define MSSIM_C1            (MSSIM_K1*MSSIM_K1)
#define MSSIM_C2            (MSSIM_K2*MSSIM_K2)


/** @brief enum of possible metrics */
typedef enum {DEFAULT_METRICS, MAX_METRIC, MSE_METRIC, RMSE_METRIC,
    PSNR_METRIC, MSSIM_METRIC} metric;

/** @brief struct of program parameters */
typedef struct
{
    /** @brief Input file A (clean) */
    char *FileA;
    /** @brief Input file B (distorted) */
    char *FileB;    
    /** @brief Quality for saving JPEG images (0 to 100) */
    int JpegQuality;
    /** @brief Metric */
    metric Metric;
    /** @brief Compute metric separately for each channel */
    int SeparateChannels;
    /** @brief Ignore boundary effects by shaving a margin of size Pad */
    int Pad;
        
    /** @brief Difference file */
    char *DifferenceFile;
    /** @brief Parameter D for creating the difference image */
    float D;
} programparams;    
    

static int ParseParams(programparams *Param, int argc, char *argv[]);
void MakeDifferenceImage(float *A, const float *B, 
    int Width, int Height, int NumChannels, float D);
void BasicMetrics(float *Max, float *Mse, const float *A, const float *B, 
    int Width, int Height, int NumChannels, int Pad);
float ComputeMssim(const float *A, const float *B, 
    int Width, int Height, int NumChannels, int Pad);
    

/** @brief Print program usage help message */
void PrintHelpMessage()
{
    printf("Image difference calculator, P. Getreuer 2010-2011\n\n");
    printf("Usage: imdiff [options] <exact file> <distorted file>\n\n"
        "Only " READIMAGE_FORMATS_SUPPORTED " images are supported.\n\n");
    printf("Options:\n");
    printf("   -m <metric>  Metric to use for comparison, choices are\n");
    printf("        max     Maximum absolute difference, max_n |A_n - B_n|\n");
    printf("        mse     Mean squared error, 1/N sum |A_n - B_n|^2\n");
    printf("        rmse    Root mean squared error, (MSE)^1/2\n");
    printf("        psnr    Peak signal-to-noise ratio, -10 log10(MSE/255^2)\n");
    printf("        mssim   Mean structural similarity index\n\n");
    printf("   -s           Compute metric separately for each channel\n");
    printf("   -p <pad>     Remove a margin of <pad> pixels before comparison\n");
    printf("   -D <number>  D parameter for difference image\n\n");    
#ifdef LIBJPEG_SUPPORT
    printf("   -q <number>   Quality for saving JPEG images (0 to 100)\n\n");
#endif    
    printf("Alternatively, a difference image is generated by the syntax\n"
           "   imdiff [-D <number>] <exact file> <distorted file> <output file>\n\n");
    printf("The difference image is computed as\n"
           "   D_n = 255/2 ((A_n - B_n)/D + 1).\n"
           "Values outside of the range [0,255] are saturated.\n\n");
    printf("Example:\n"
#ifdef LIBPNG_SUPPORT
        "   imdiff -mpsnr frog-exact.png frog-4x.bmp\n");
#else
        "   imdiff -mpsnr frog-exact.bmp frog-4x.bmp\n");
#endif
}   


int main(int argc, char *argv[])
{
    struct
    {
        float *Data;
        int Width;
        int Height;
    } A = {NULL, 0, 0}, B = {NULL, 0, 0};

    programparams Param;
    float Max, MaxC[3], Mse, MseC[3], Mssim;
    int Channel, Status = 1;
    
           
    if(!ParseParams(&Param, argc, argv))
        return 0;
    
    /* Read the exact image */
    if(!(A.Data = (float *)ReadImage(&A.Width, &A.Height, Param.FileA, 
        IMAGEIO_FLOAT | IMAGEIO_RGB | IMAGEIO_PLANAR)))
        goto Catch;
    
    /* Read the distorted image */
    if(!(B.Data = (float *)ReadImage(&B.Width, &B.Height, Param.FileB, 
        IMAGEIO_FLOAT | IMAGEIO_RGB | IMAGEIO_PLANAR)))
        goto Catch;
    
    if(A.Width != B.Width || A.Height != B.Height)
    {
        ErrorMessage("Image sizes don't match, %dx%d vs. %dx%d.\n", 
            A.Width, A.Height, B.Width, B.Height);
        goto Catch;
    }
    else if(A.Width <= 2*Param.Pad || A.Height <= 2*Param.Pad)
    {
        ErrorMessage(
            "Removal of %d-pixel padding removes entire %dx%d image.\n",
            Param.Pad, A.Width, A.Height);
        goto Catch;
    }
    
    if(Param.DifferenceFile)
    {
        MakeDifferenceImage(A.Data, B.Data, A.Width, A.Height, 3, Param.D);
        
        if(!(WriteImage(A.Data, A.Width, A.Height, Param.DifferenceFile, 
            IMAGEIO_FLOAT | IMAGEIO_RGB | IMAGEIO_PLANAR, Param.JpegQuality)))
            goto Catch;
    }
    else
    {
        Max = 0;
        Mse = 0;
        
        for(Channel = 0; Channel < 3; Channel++)
        {
            BasicMetrics(&MaxC[Channel], &MseC[Channel], 
                    A.Data + Channel*A.Width*A.Height, 
                    B.Data + Channel*B.Width*B.Height, 
                    A.Width, A.Height, 1, Param.Pad);
           
            if(MaxC[Channel] > Max)
                Max = MaxC[Channel];
            
            Mse += MseC[Channel];
        }
        
        Mse /= 3;
        
        switch(Param.Metric)
        {
            case DEFAULT_METRICS:
                if(!Param.SeparateChannels)
                {
                    printf("Maximum absolute difference:  %g\n", DISPLAY_SCALING*Max);
                    printf("Peak signal-to-noise ratio:   %.4f\n", -10*log10(Mse));
                }
                else
                {
                    printf("Maximum absolute difference:  %g %g %g\n", 
                        DISPLAY_SCALING*MaxC[0], DISPLAY_SCALING*MaxC[1],
                        DISPLAY_SCALING*MaxC[2]);
                    printf("Peak signal-to-noise ratio:   %.4f %.4f %.4f\n", 
                        -10*log10(MseC[0]), -10*log10(MseC[1]), -10*log10(MseC[2]));
                }
                
                if(A.Width <= 2*(5 + Param.Pad) 
                    || A.Height <= 2*(5 + Param.Pad))
                    printf("Image size is too small to compute MSSIM.\n");
                else
                {
                    
                    Mssim = (Max == 0) ? 1 : ComputeMssim(A.Data, B.Data, 
                            A.Width, A.Height, 3, Param.Pad);
                
                    if(Mssim != -1)
                        printf("Mean structural similarity:   %.4f\n", Mssim);
                }
                break;
            case MAX_METRIC:
                if(!Param.SeparateChannels)
                    printf("%g\n", DISPLAY_SCALING*Max);
                else
                    printf("%g %g %g\n", DISPLAY_SCALING*MaxC[0], 
                        DISPLAY_SCALING*MaxC[1], DISPLAY_SCALING*MaxC[2]);
                break;
            case MSE_METRIC:
                if(!Param.SeparateChannels)
                    printf("%.4f\n", DISPLAY_SCALING*DISPLAY_SCALING*Mse);
                else
                    printf("%.4f %.4f %.4f\n", 
                        DISPLAY_SCALING*DISPLAY_SCALING*MseC[0],
                        DISPLAY_SCALING*DISPLAY_SCALING*MseC[1],
                        DISPLAY_SCALING*DISPLAY_SCALING*MseC[2]);
                break;
            case RMSE_METRIC:
                if(!Param.SeparateChannels)
                    printf("%.4f\n", DISPLAY_SCALING*sqrt(Mse));
                else
                    printf("%.4f %.4f %.4f\n", 
                        DISPLAY_SCALING*sqrt(MseC[0]),
                        DISPLAY_SCALING*sqrt(MseC[1]),
                        DISPLAY_SCALING*sqrt(MseC[2]));
                break;
            case PSNR_METRIC:
                if(!Param.SeparateChannels)
                    printf("%.4f\n", -10*log10(Mse));
                else
                printf("%.4f %.4f %.4f\n", 
                    -10*log10(MseC[0]), -10*log10(MseC[1]), -10*log10(MseC[2]));
                break;            
            case MSSIM_METRIC:
                if(A.Width <= 2*(5 + Param.Pad) 
                    || A.Height <= 2*(5 + Param.Pad))
                    printf("Image size is too small to compute MSSIM.\n");
                else
                {
                    Mssim = (Max == 0) ? 1 : ComputeMssim(A.Data, B.Data, 
                            A.Width, A.Height, 3, Param.Pad);
                
                    if(Mssim == -1)
                        ErrorMessage("Memory allocation failed.\n");
                    else                
                        printf("%.4f\n", Mssim);
                }
                break;
        }
    }
    
    Status = 0; /* Finished successfully */
Catch:
    Free(B.Data);
    Free(A.Data);
    return Status;
}


/** @brief Make a difference image, Diff = (A - B)/(2D) + 0.5 */
void MakeDifferenceImage(float *A, const float *B, 
    int Width, int Height, int NumChannels, float D)
{
    const int NumEl = NumChannels*Width*Height;
    int n;
    
    D = (2*D)/255;
    
    for(n = 0; n < NumEl; n++)
        A[n] = (A[n] - B[n])/D + (float)0.5;
}


/** @brief Compute the maximum absolute difference and the MSE */
void BasicMetrics(float *Max, float *Mse, const float *A, const float *B, 
    int Width, int Height, int NumChannels, int Pad)
{
    float Diff, CurMax = 0;
    double AccumMse = 0;
    int x, y, Channel, n;
    
    
    for(Channel = 0; Channel < NumChannels; Channel++)
        for(y = Pad; y < Height - Pad; y++)
            for(x = Pad; x < Width - Pad; x++)
            {
                n = x + Width*(y + Height*Channel);                
                Diff = (float)fabs(A[n] - B[n]);
                    
                if(CurMax < Diff)
                    CurMax = Diff;
                
                AccumMse += Diff*Diff;
            }
    
    *Max = CurMax;
    *Mse = (float)(AccumMse / (NumChannels*(Width - 2*Pad)*(Height - 2*Pad)));
}


/** @brief Compute the Mean Structural SIMilarity (MSSIM) index */
float ComputeMssim(const float *A, const float *B, 
    int Width, int Height, int NumChannels, int Pad)
{   
    /* 11-tap Gaussian filter with standard deviation 1.5 */
    const int R = 5;
    filter Window = GaussianFilter(1.5, R);    
    /* Boundary does not matter, convolution is used only in the interior */
    boundaryext Boundary = GetBoundaryExt("zpd");
    
    const int NumPixels = Width*Height;
    const int NumEl = NumChannels*NumPixels;
    float *Buffer = NULL, *MuA = NULL, *MuB = NULL, 
        *MuAA = NULL, *MuBB = NULL, *MuAB = NULL;
    double MuASqr, MuBSqr, MuAMuB, 
        SigmaASqr, SigmaBSqr, SigmaAB, Mssim = -1;
    int n, x, y, c; 
    
    
    if(IsNullFilter(Window)
        || !(Buffer = (float *)Malloc(sizeof(float)*NumPixels))
        || !(MuA = (float *)Malloc(sizeof(float)*NumEl))
        || !(MuB = (float *)Malloc(sizeof(float)*NumEl))
        || !(MuAA = (float *)Malloc(sizeof(float)*NumEl))
        || !(MuBB = (float *)Malloc(sizeof(float)*NumEl))
        || !(MuAB = (float *)Malloc(sizeof(float)*NumEl)))
        goto Catch;
    
    SeparableConv2D(MuA, Buffer, A, Window, Window, 
        Boundary, Width, Height, NumChannels);        
    SeparableConv2D(MuB, Buffer, B, Window, Window, 
        Boundary, Width, Height, NumChannels);
    
    for(n = 0; n < NumEl; n++)
    {        
        MuAA[n] = A[n]*A[n];
        MuBB[n] = B[n]*B[n];
        MuAB[n] = A[n]*B[n];
    }
    
    SeparableConv2D(MuAA, Buffer, MuAA, Window, Window, 
        Boundary, Width, Height, NumChannels);
    SeparableConv2D(MuBB, Buffer, MuBB, Window, Window, 
        Boundary, Width, Height, NumChannels);
    SeparableConv2D(MuAB, Buffer, MuAB, Window, Window, 
        Boundary, Width, Height, NumChannels);
    Mssim = 0;
    
    Pad += R;
    
    for(c = 0; c < NumChannels; c++)
        for(y = Pad; y < Height - Pad; y++)
            for(x = Pad; x < Width - Pad; x++)            
            {
                n = x + Width*(y + Height*c);
                MuASqr = MuA[n]*MuA[n];
                MuBSqr = MuB[n]*MuB[n];
                MuAMuB = MuA[n]*MuB[n];
                SigmaASqr = MuAA[n] - MuASqr;
                SigmaBSqr = MuBB[n] - MuBSqr;
                SigmaAB = MuAB[n] - MuAMuB;
                
                Mssim += ((2*MuAMuB + MSSIM_C1)*(2*SigmaAB + MSSIM_C2))
                    / ((MuASqr + MuBSqr + MSSIM_C1)
                        *(SigmaASqr + SigmaBSqr + MSSIM_C2));
            }
    
    Mssim /= NumChannels*(Width - 2*Pad)*(Height - 2*Pad);
    
Catch:
    FreeFilter(Window);
    Free(MuAB);
    Free(MuBB);
    Free(MuAA);
    Free(MuB);
    Free(MuA);
    Free(Buffer);
    return (float)Mssim;
}



static int ParseParams(programparams *Param, int argc, char *argv[])
{
    char *OptionString;
    char OptionChar;
    int i;

    
    if(argc < 2)
    {
        PrintHelpMessage();
        return 0;
    }
    
    /* Set parameter defaults */
    Param->FileA = NULL;
    Param->FileB = NULL;    
    Param->Metric = DEFAULT_METRICS;    
    Param->SeparateChannels = 0;
    
    Param->Pad = 0;    
    Param->DifferenceFile = NULL;
    Param->JpegQuality = 95;
    Param->D = 20;
        
    for(i = 1; i < argc;)
    {
        if(argv[i] && argv[i][0] == '-')
        {
            if((OptionChar = argv[i][1]) == 0)
            {
                ErrorMessage("Invalid parameter format.\n");
                return 0;
            }

            if(argv[i][2])
                OptionString = &argv[i][2];
            else if(++i < argc)
                OptionString = argv[i];
            else
            {
                ErrorMessage("Invalid parameter format.\n");
                return 0;
            }
            
            switch(OptionChar)
            {
            case 'p':
                Param->Pad = atoi(OptionString);
                
                if(Param->Pad < 0)
                {
                    ErrorMessage("Pad must be nonnegative.\n");
                    return 0;
                }
                break;
            case 's':
                Param->SeparateChannels = 1;
                i--;
                break;
            case 'D':
                Param->D = (float)atof(OptionString);

                if(Param->D <= 0)
                {
                    ErrorMessage("D must be positive.\n");
                    return 0;
                }
                break;
            case 'm':
                if(!strcmp(OptionString, "max"))
                    Param->Metric = MAX_METRIC;
                else if(!strcmp(OptionString, "mse"))
                    Param->Metric = MSE_METRIC;
                else if(!strcmp(OptionString, "rmse"))
                    Param->Metric = RMSE_METRIC;
                else if(!strcmp(OptionString, "psnr"))
                    Param->Metric = PSNR_METRIC;
                else if(!strcmp(OptionString, "mssim"))
                    Param->Metric = MSSIM_METRIC;
                else
                    ErrorMessage("Unknown metric.\n");
                break;
                
#ifdef LIBJPEG_SUPPORT
            case 'q':
                Param->JpegQuality = atoi(OptionString);

                if(Param->JpegQuality <= 0 || Param->JpegQuality > 100)
                {
                    ErrorMessage("JPEG quality must be between 0 and 100.\n");
                    return 0;
                }
                break;
#endif
            case '-':
                PrintHelpMessage();
                return 0;
            default:
                if(isprint(OptionChar))
                    ErrorMessage("Unknown option \"-%c\".\n", OptionChar);
                else
                    ErrorMessage("Unknown option.\n");

                return 0;
            }

            i++;
        }
        else
        {
            if(!Param->FileA)
                Param->FileA = argv[i];
            else if(!Param->FileB)
                Param->FileB = argv[i];
            else
                Param->DifferenceFile = argv[i];

            i++;
        }
    }
    
    if(!Param->FileA || !Param->FileB)
    {
        PrintHelpMessage();
        return 0;
    }
    
    return 1;
}
