#import <Cocoa/Cocoa.h>
#import <CoreImage/CoreImage.h>
#import <ImageIO/ImageIO.h>
#import <CoreServices/CoreServices.h>

// Helper to generate scaled QR Code CGImage
CGImageRef createScaledQRImage(NSString *text) {
    NSData *data = [text dataUsingEncoding:NSUTF8StringEncoding];
    CIFilter *filter = [CIFilter filterWithName:@"CIQRCodeGenerator"];
    [filter setValue:data forKey:@"inputMessage"];
    [filter setValue:@"M" forKey:@"inputCorrectionLevel"]; // Medium error correction
    
    CIImage *ciImage = filter.outputImage;
    if (!ciImage) return nil;
    
    // Scale the image up (CIQRCodeGenerator outputs a tiny image)
    CGFloat scaleX = 450.0 / ciImage.extent.size.width;
    CGFloat scaleY = 450.0 / ciImage.extent.size.height;
    CIImage *scaledImage = [ciImage imageByApplyingTransform:CGAffineTransformMakeScale(scaleX, scaleY)];
    
    CIContext *context = [CIContext contextWithOptions:nil];
    return [context createCGImage:scaledImage fromRect:scaledImage.extent];
}

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        NSString *text = @"";
        
        // 1. Check arguments
        if (argc > 1) {
            NSMutableArray *args = [NSMutableArray array];
            for (int i = 1; i < argc; i++) {
                [args addObject:[NSString stringWithUTF8String:argv[i]]];
            }
            text = [args componentsJoinedByString:@" "];
        } else {
            // 2. Check stdin
            if (!isatty(STDIN_FILENO)) {
                NSData *inputData = [[NSFileHandle fileHandleWithStandardInput] readDataToEndOfFile];
                text = [[NSString alloc] initWithData:inputData encoding:NSUTF8StringEncoding];
            }
            
            // 3. Check clipboard if still empty
            if (!text || [text stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]].length == 0) {
                NSPasteboard *pc = [NSPasteboard generalPasteboard];
                text = [pc stringForType:NSPasteboardTypeString];
            }
        }
        
        text = [text stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        
        if (!text || text.length == 0) {
            fprintf(stderr, "Error: Input text is empty. Please copy some text to clipboard, pass it as an argument, or pipe it to stdin.\n");
            return 1;
        }
        
        // Chunk the text into parts of 100 characters (low density = very easy to scan)
        NSUInteger chunkSize = 100;
        NSMutableArray *chunks = [NSMutableArray array];
        NSUInteger length = text.length;
        for (NSUInteger i = 0; i < length; i += chunkSize) {
            NSRange range = NSMakeRange(i, MIN(chunkSize, length - i));
            [chunks addObject:[text substringWithRange:range]];
        }
        
        NSUInteger total = chunks.count;
        NSMutableArray *images = [NSMutableArray array];
        
        for (NSUInteger i = 0; i < total; i++) {
            NSString *formatted = [NSString stringWithFormat:@"%lu/%lu:%@", i + 1, total, chunks[i]];
            CGImageRef img = createScaledQRImage(formatted);
            if (img) {
                [images addObject:(__bridge id)img];
                CGImageRelease(img);
            } else {
                fprintf(stderr, "Error: Failed to generate QR code for chunk %lu.\n", i + 1);
                return 1;
            }
        }
        
        NSString *tempDir = NSTemporaryDirectory();
        NSString *outputPath = [tempDir stringByAppendingPathComponent:@"qr_transfer.gif"];
        NSURL *outputURL = [NSURL fileURLWithPath:outputPath];
        
        CGImageDestinationRef destination = CGImageDestinationCreateWithURL((__bridge CFURLRef)outputURL, kUTTypeGIF, images.count, nil);
        if (!destination) {
            fprintf(stderr, "Error: Failed to create image destination.\n");
            return 1;
        }
        
        // Loop count of 0 = loop forever
        NSDictionary *fileProperties = @{
            (NSString *)kCGImagePropertyGIFDictionary: @{
                (NSString *)kCGImagePropertyGIFLoopCount: @0
            }
        };
        CGImageDestinationSetProperties(destination, (__bridge CFDictionaryRef)fileProperties);
        
        // Delay: 0.25 seconds per frame
        NSDictionary *frameProperties = @{
            (NSString *)kCGImagePropertyGIFDictionary: @{
                (NSString *)kCGImagePropertyGIFDelayTime: @0.25
            }
        };
        
        for (id imgObj in images) {
            CGImageRef img = (__bridge CGImageRef)imgObj;
            CGImageDestinationAddImage(destination, img, (__bridge CFDictionaryRef)frameProperties);
        }
        
        if (CGImageDestinationFinalize(destination)) {
            printf("%s\n", [outputPath UTF8String]);
        } else {
            fprintf(stderr, "Error: Failed to finalize GIF.\n");
            CFRelease(destination);
            return 1;
        }
        
        CFRelease(destination);
    }
    return 0;
}
