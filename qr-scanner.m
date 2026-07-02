#import <Cocoa/Cocoa.h>
#import <AVFoundation/AVFoundation.h>
#import <CoreImage/CoreImage.h>
#import <CoreMedia/CoreMedia.h>
#import <CoreVideo/CoreVideo.h>

@interface ScannerOverlayView : NSView
@property (nonatomic, assign) CGFloat progress;
@property (nonatomic, retain) NSString *statusText;
@property (nonatomic, assign) CGFloat scanLineY;
@property (nonatomic, assign) CGFloat scanLineDirection;
@property (nonatomic, retain) NSTimer *timer;
@end

@implementation ScannerOverlayView

- (instancetype)initWithFrame:(NSRect)frameRect {
    self = [super initWithFrame:frameRect];
    if (self) {
        self.wantsLayer = YES;
        self.progress = 0.0;
        self.statusText = @"Align camera with the QR code...";
        self.scanLineY = 60.0;
        self.scanLineDirection = 1.0;
        
        __weak typeof(self) weakSelf = self;
        self.timer = [NSTimer scheduledTimerWithTimeInterval:0.03 repeats:YES block:^(NSTimer * _Nonnull timer) {
            [weakSelf updateScanLine];
        }];
    }
    return self;
}

- (void)dealloc {
    [_timer invalidate];
}

- (void)updateScanLine {
    CGFloat height = self.bounds.size.height;
    self.scanLineY += self.scanLineDirection * 3.5;
    if (self.scanLineY >= height - 60 || self.scanLineY <= 60) {
        self.scanLineDirection *= -1;
    }
    self.needsDisplay = YES;
}

- (void)drawRect:(NSRect)dirtyRect {
    [super drawRect:dirtyRect];
    
    CGContextRef ctx = [[NSGraphicsContext currentContext] CGContext];
    if (!ctx) return;
    
    CGFloat width = self.bounds.size.width;
    CGFloat height = self.bounds.size.height;
    
    // 1. Draw Scanner Corners (Reticle) in the center
    CGFloat reticleSize = 280.0;
    CGRect reticleRect = CGRectMake((width - reticleSize) / 2.0, (height - reticleSize) / 2.0, reticleSize, reticleSize);
    
    CGContextSetStrokeColorWithColor(ctx, [[NSColor systemGreenColor] colorWithAlphaComponent:0.6].CGColor);
    CGContextSetLineWidth(ctx, 4.0);
    
    CGFloat cornerLen = 30.0;
    
    // Top-left corner
    CGContextMoveToPoint(ctx, reticleRect.origin.x, CGRectGetMaxY(reticleRect) - cornerLen);
    CGContextAddLineToPoint(ctx, reticleRect.origin.x, CGRectGetMaxY(reticleRect));
    CGContextAddLineToPoint(ctx, reticleRect.origin.x + cornerLen, CGRectGetMaxY(reticleRect));
    
    // Top-right corner
    CGContextMoveToPoint(ctx, CGRectGetMaxX(reticleRect) - cornerLen, CGRectGetMaxY(reticleRect));
    CGContextAddLineToPoint(ctx, CGRectGetMaxX(reticleRect), CGRectGetMaxY(reticleRect));
    CGContextAddLineToPoint(ctx, CGRectGetMaxX(reticleRect), CGRectGetMaxY(reticleRect) - cornerLen);
    
    // Bottom-right corner
    CGContextMoveToPoint(ctx, CGRectGetMaxX(reticleRect), reticleRect.origin.y + cornerLen);
    CGContextAddLineToPoint(ctx, CGRectGetMaxX(reticleRect), reticleRect.origin.y);
    CGContextAddLineToPoint(ctx, CGRectGetMaxX(reticleRect) - cornerLen, reticleRect.origin.y);
    
    // Bottom-left corner
    CGContextMoveToPoint(ctx, reticleRect.origin.x + cornerLen, reticleRect.origin.y);
    CGContextAddLineToPoint(ctx, reticleRect.origin.x, reticleRect.origin.y);
    CGContextAddLineToPoint(ctx, reticleRect.origin.x, reticleRect.origin.y + cornerLen);
    
    CGContextStrokePath(ctx);
    
    // 2. Draw Moving Scan Line
    CGContextSetStrokeColorWithColor(ctx, [[NSColor systemGreenColor] colorWithAlphaComponent:0.8].CGColor);
    CGContextSetLineWidth(ctx, 2.0);
    CGContextMoveToPoint(ctx, reticleRect.origin.x + 10, self.scanLineY);
    CGContextAddLineToPoint(ctx, CGRectGetMaxX(reticleRect) - 10, self.scanLineY);
    CGContextStrokePath(ctx);
    
    // Draw linear gradient glow behind the scan line
    const CGFloat colors[] = {
        0.0, 1.0, 0.0, 0.25,
        0.0, 1.0, 0.0, 0.0
    };
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    CGGradientRef gradient = CGGradientCreateWithColorComponents(colorSpace, colors, NULL, 2);
    if (gradient) {
        CGContextDrawLinearGradient(ctx,
                                    gradient,
                                    CGPointMake(width / 2.0, self.scanLineY),
                                    CGPointMake(width / 2.0, self.scanLineY - self.scanLineDirection * 18.0),
                                    0);
        CGGradientRelease(gradient);
    }
    CGColorSpaceRelease(colorSpace);
    
    // 3. Draw Bottom UI Card (Glassmorphism overlay)
    CGRect uiBoxRect = CGRectMake(40, 30, width - 80, 80);
    NSBezierPath *path = [NSBezierPath bezierPathWithRoundedRect:uiBoxRect xRadius:16 yRadius:16];
    [[[NSColor blackColor] colorWithAlphaComponent:0.65] set];
    [path fill];
    
    [[[NSColor whiteColor] colorWithAlphaComponent:0.15] set];
    [path setLineWidth:1.0];
    [path stroke];
    
    // 4. Draw Status Text
    NSMutableParagraphStyle *textStyle = [[NSMutableParagraphStyle alloc] init];
    textStyle.alignment = NSTextAlignmentCenter;
    NSFont *textFont = [NSFont systemFontOfSize:13 weight:NSFontWeightSemibold];
    NSDictionary *textAttrs = @{
        NSFontAttributeName: textFont,
        NSForegroundColorAttributeName: [NSColor whiteColor],
        NSParagraphStyleAttributeName: textStyle
    };
    
    CGRect textRect = CGRectMake(uiBoxRect.origin.x + 10, CGRectGetMaxY(uiBoxRect) - 32, uiBoxRect.size.width - 20, 22);
    [self.statusText drawInRect:textRect withAttributes:textAttrs];
    
    // 5. Draw Progress Bar Background
    CGRect pBarBgRect = CGRectMake(uiBoxRect.origin.x + 30, uiBoxRect.origin.y + 18, uiBoxRect.size.width - 60, 8);
    NSBezierPath *bgPath = [NSBezierPath bezierPathWithRoundedRect:pBarBgRect xRadius:4 yRadius:4];
    [[[NSColor whiteColor] colorWithAlphaComponent:0.12] set];
    [bgPath fill];
    
    // Draw Progress Bar Fill
    if (self.progress > 0) {
        CGRect pBarFillRect = CGRectMake(pBarBgRect.origin.x, pBarBgRect.origin.y, pBarBgRect.size.width * self.progress, 8);
        NSBezierPath *fillPath = [NSBezierPath bezierPathWithRoundedRect:pBarFillRect xRadius:4 yRadius:4];
        [[NSColor systemGreenColor] set];
        [fillPath fill];
    }
}
@end

@interface AppDelegate : NSObject <NSApplicationDelegate, NSWindowDelegate, AVCaptureVideoDataOutputSampleBufferDelegate>
@property (nonatomic, retain) NSWindow *window;
@property (nonatomic, retain) AVCaptureSession *captureSession;
@property (nonatomic, retain) AVCaptureVideoPreviewLayer *previewLayer;
@property (nonatomic, retain) ScannerOverlayView *overlayView;
@property (nonatomic, retain) AVCaptureVideoDataOutput *videoDataOutput;
@property (nonatomic, retain) dispatch_queue_t videoQueue;

// Chunk tracking
@property (nonatomic, retain) NSMutableDictionary *receivedChunks;
@property (nonatomic, assign) NSInteger totalChunks;
@end

@implementation AppDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    self.receivedChunks = [NSMutableDictionary dictionary];
    self.totalChunks = -1;
    
    CGFloat windowWidth = 640.0;
    CGFloat windowHeight = 480.0;
    
    NSRect screenRect = [[NSScreen mainScreen] frame];
    NSRect windowRect = NSMakeRect((screenRect.size.width - windowWidth) / 2.0,
                                   (screenRect.size.height - windowHeight) / 2.0,
                                   windowWidth,
                                   windowHeight);
    
    self.window = [[NSWindow alloc] initWithContentRect:windowRect
                                              styleMask:(NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskFullSizeContentView)
                                                backing:NSBackingStoreBuffered
                                                  defer:NO];
    self.window.title = @"Offline Text Scanner";
    self.window.titlebarAppearsTransparent = YES;
    self.window.titleVisibility = NSWindowTitleHidden;
    self.window.level = NSFloatingWindowLevel;
    self.window.delegate = self;
    self.window.movableByWindowBackground = YES;
    
    NSView *contentView = [[NSView alloc] initWithFrame:self.window.contentView.bounds];
    contentView.wantsLayer = YES;
    contentView.layer.backgroundColor = [NSColor blackColor].CGColor;
    self.window.contentView = contentView;
    
    [self setupCamera];
    
    self.overlayView = [[ScannerOverlayView alloc] initWithFrame:contentView.bounds];
    self.overlayView.autoresizingMask = (NSViewWidthSizable | NSViewHeightSizable);
    [contentView addSubview:self.overlayView];
    
    [self.window makeKeyAndOrderFront:nil];
    [NSApp activateIgnoringOtherApps:YES];
}

- (void)setupCamera {
    self.captureSession = [[AVCaptureSession alloc] init];
    self.captureSession.sessionPreset = AVCaptureSessionPreset640x480;
    
    AVCaptureDevice *videoDevice = [AVCaptureDevice defaultDeviceWithMediaType:AVMediaTypeVideo];
    if (!videoDevice) {
        [self showErrorAndExit:@"No camera device found."];
        return;
    }
    
    NSError *error = nil;
    AVCaptureDeviceInput *videoInput = [AVCaptureDeviceInput deviceInputWithDevice:videoDevice error:&error];
    if (error || !videoInput) {
        [self showErrorAndExit:[NSString stringWithFormat:@"Cannot init camera: %@", error.localizedDescription]];
        return;
    }
    
    if ([self.captureSession canAddInput:videoInput]) {
        [self.captureSession addInput:videoInput];
    } else {
        [self showErrorAndExit:@"Cannot add video camera input."];
        return;
    }
    
    self.videoDataOutput = [[AVCaptureVideoDataOutput alloc] init];
    self.videoDataOutput.alwaysDiscardsLateVideoFrames = YES;
    self.videoQueue = dispatch_queue_create("videoQueue", DISPATCH_QUEUE_SERIAL);
    [self.videoDataOutput setSampleBufferDelegate:self queue:self.videoQueue];
    
    if ([self.captureSession canAddOutput:self.videoDataOutput]) {
        [self.captureSession addOutput:self.videoDataOutput];
    }
    
    self.previewLayer = [AVCaptureVideoPreviewLayer layerWithSession:self.captureSession];
    self.previewLayer.videoGravity = AVLayerVideoGravityResizeAspectFill;
    self.previewLayer.frame = self.window.contentView.bounds;
    [self.window.contentView.layer addSublayer:self.previewLayer];
    
    AVAuthorizationStatus status = [AVCaptureDevice authorizationStatusForMediaType:AVMediaTypeVideo];
    if (status == AVAuthorizationStatusAuthorized) {
        [self.captureSession startRunning];
    } else if (status == AVAuthorizationStatusNotDetermined) {
        __weak typeof(self) weakSelf = self;
        [AVCaptureDevice requestAccessForMediaType:AVMediaTypeVideo completionHandler:^(BOOL granted) {
            dispatch_async(dispatch_get_main_queue(), ^{
                if (granted) {
                    [weakSelf.captureSession startRunning];
                } else {
                    [weakSelf showErrorAndExit:@"Camera access permission denied."];
                }
            });
        }];
    } else {
        [self showErrorAndExit:@"Camera access is restricted or denied."];
    }
}

- (void)captureOutput:(AVCaptureOutput *)output didOutputSampleBuffer:(CMSampleBufferRef)sampleBuffer fromConnection:(AVCaptureConnection *)connection {
    CVImageBufferRef imageBuffer = CMSampleBufferGetImageBuffer(sampleBuffer);
    if (!imageBuffer) return;
    
    CIImage *ciImage = [CIImage imageWithCVImageBuffer:imageBuffer];
    
    NSDictionary *options = @{CIDetectorAccuracy: CIDetectorAccuracyHigh};
    CIDetector *detector = [CIDetector detectorOfType:CIDetectorTypeQRCode context:nil options:options];
    
    NSArray *features = [detector featuresInImage:ciImage];
    for (CIFeature *feature in features) {
        if ([feature isKindOfClass:[CIQRCodeFeature class]]) {
            CIQRCodeFeature *qrFeature = (CIQRCodeFeature *)feature;
            NSString *message = qrFeature.messageString;
            if (message) {
                [self processQRCodeMessage:message];
            }
        }
    }
}

- (void)processQRCodeMessage:(NSString *)message {
    NSString *pattern = @"^(\\d+)/(\\d+):(.*)$";
    NSError *error = nil;
    NSRegularExpression *regex = [NSRegularExpression regularExpressionWithPattern:pattern
                                                                           options:NSRegularExpressionDotMatchesLineSeparators
                                                                             error:&error];
    if (error || !regex) return;
    
    NSTextCheckingResult *match = [regex firstMatchInString:message options:0 range:NSMakeRange(0, message.length)];
    if (!match) return;
    
    NSString *indexStr = [message substringWithRange:[match rangeAtIndex:1]];
    NSString *totalStr = [message substringWithRange:[match rangeAtIndex:2]];
    NSString *payload = [message substringWithRange:[match rangeAtIndex:3]];
    
    NSInteger index = [indexStr integerValue];
    NSInteger total = [totalStr integerValue];
    
    dispatch_async(dispatch_get_main_queue(), ^{
        [self handleChunkReceivedWithIndex:index total:total payload:payload];
    });
}

- (void)handleChunkReceivedWithIndex:(NSInteger)index total:(NSInteger)total payload:(NSString *)payload {
    if (self.totalChunks != -1 && self.totalChunks != total) {
        [self.receivedChunks removeAllObjects];
    }
    self.totalChunks = total;
    
    NSNumber *key = @(index);
    if (!self.receivedChunks[key]) {
        self.receivedChunks[key] = payload;
        
        // Play audio feedback for successful chunk detection
        [[NSSound soundNamed:@"Tink"] play];
        
        CGFloat progressRatio = (CGFloat)self.receivedChunks.count / (CGFloat)total;
        self.overlayView.progress = progressRatio;
        self.overlayView.statusText = [NSString stringWithFormat:@"Received chunk %lu of %ld...", (unsigned long)self.receivedChunks.count, (long)total];
        self.overlayView.needsDisplay = YES;
        
        if (self.receivedChunks.count == total) {
            [self finishScanning];
        }
    }
}

- (void)finishScanning {
    [self.captureSession stopRunning];
    
    NSMutableString *fullText = [NSMutableString string];
    for (NSInteger i = 1; i <= self.totalChunks; i++) {
        NSString *chunk = self.receivedChunks[@(i)];
        if (chunk) {
            [fullText appendString:chunk];
        }
    }
    
    NSPasteboard *pc = [NSPasteboard generalPasteboard];
    [pc clearContents];
    [pc setString:fullText forType:NSPasteboardTypeString];
    
    [[NSSound soundNamed:@"Glass"] play];
    
    self.overlayView.statusText = @"Complete! Copied to clipboard.";
    self.overlayView.progress = 1.0;
    self.overlayView.needsDisplay = YES;
    
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.6 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
        [NSApp terminate:nil];
    });
}

- (void)showErrorAndExit:(NSString *)message {
    dispatch_async(dispatch_get_main_queue(), ^{
        fprintf(stderr, "Error: %s\n", [message UTF8String]);
        NSAlert *alert = [[NSAlert alloc] init];
        alert.messageText = @"QR Scanner Error";
        alert.informativeText = message;
        alert.alertStyle = NSAlertStyleCritical;
        [alert addButtonWithTitle:@"OK"];
        [alert runModal];
        [NSApp terminate:nil];
    });
}

- (BOOL)windowShouldClose:(NSWindow *)sender {
    [NSApp terminate:nil];
    return YES;
}
@end

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        NSApplication *app = [NSApplication sharedApplication];
        AppDelegate *delegate = [[AppDelegate alloc] init];
        app.delegate = delegate;
        [app setActivationPolicy:NSApplicationActivationPolicyAccessory];
        [app run];
    }
    return 0;
}
