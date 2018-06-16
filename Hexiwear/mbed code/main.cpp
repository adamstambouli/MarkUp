#include "mbed.h"
#include "rtos.h"
#include "FXOS8700.h"
#include "FXAS21002.h"
#include "Hexi_KW40Z.h"
#include "Hexi_OLED_SSD1351.h"
#include "string.h"

#define LED_ON      0
#define LED_OFF     1

void StartHaptic(void);
void StopHaptic(void const *n);
void txTask(void);
void displayTask(void);

DigitalOut redLed(LED1,1);
DigitalOut greenLed(LED2,1);
DigitalOut blueLed(LED3,1);
DigitalOut haptic(PTB9);

/* Define timer for haptic feedback */
RtosTimer hapticTimer(StopHaptic, osTimerOnce);

/* Instantiate the Hexi KW40Z Driver (UART TX, UART RX) */ 
KW40Z kw40z_device(PTE24, PTE25);

/*Create a Thread to handle sending Sensor Data */ 
Thread txThread;

/* Instantiate the SSD1351 OLED Driver */ 
SSD1351 oled(PTB22,PTB21,PTC13,PTB20,PTE6, PTD15); /* (MOSI,SCLK,POWER,CS,RST,DC) */

// Initialize Serial port
Serial RPi(PTD3, PTD2);
Serial pc(USBTX, USBRX);

// Pin connections & address for Hexiwear
FXOS8700 accel(PTC11, PTC10);
FXOS8700 mag(PTC11, PTC10);
FXAS21002 gyro(PTC11,PTC10);


Timer stopwatch;
float checktime;
char text[20]; 
int tx_flag = 0;
float accel_data[3];
float mag_data[3];
float gyro_data[3];
Thread displayThread;
int counter = 0;
int status = 0;

/****************************Call Back Functions*******************************/
void ButtonDown(void)
{
    StartHaptic();
    kw40z_device.ToggleAdvertisementMode();
}

void ButtonUp(void)
{
    StartHaptic();
    kw40z_device.ToggleAdvertisementMode();

}
 
void ButtonRight(void)
{
    StartHaptic();
    
    if (tx_flag == 0) {
        /*Start transmitting Sensor Data */
        txThread.start(txTask); 
        tx_flag = 1;
        pc.printf("Started Data TX\r\n");
        greenLed = LED_OFF;
        redLed = LED_ON;
    }
    else if (tx_flag == 1) {
        /*Stop transmitting Sensor Data */
        tx_flag = 0;
        pc.printf("Stopped Data TX\r\n");
        redLed = LED_OFF;
        greenLed = LED_ON;
    }
}
 
void ButtonLeft(void)
{
    StartHaptic();
    
    if (tx_flag == 0) {
        
        /*Start transmitting Sensor Data */
        txThread.start(txTask); 
        tx_flag = 1;
        pc.printf("Started Data TX\r\n");
        greenLed = LED_OFF;
        redLed = LED_ON;
    }
    else if (tx_flag == 1) {
        /*Stop transmitting Sensor Data */
        tx_flag = 0;
        pc.printf("Stopped Data TX\r\n");
        redLed = LED_OFF;
        greenLed = LED_ON;
    }
}
 


int main()
{
    /* Register callbacks to application functions */

    kw40z_device.attach_buttonLeft(&ButtonLeft);
    kw40z_device.attach_buttonRight(&ButtonRight);
    kw40z_device.attach_buttonUp(&ButtonUp);
    kw40z_device.attach_buttonDown(&ButtonDown);

    /*Start displaying data on OLED */
    displayThread.start(displayTask); 
       
    pc.printf("hello\n\r");
    
    
    
    // Configure Accelerometer/Magnetometer FXOS8700, Gyroscope FXAS21002
    accel.accel_config();
    mag.mag_config();
    gyro.gyro_config();


    
    RPi.baud(9600);

    stopwatch.reset();
    stopwatch.start();
    
    wait(0.5);

    while (true) {
      Thread::wait(500);
    }
    
    
}


/******************************End of Main*************************************/

void StartHaptic(void)  {
    hapticTimer.start(50);
    haptic = 1;
}

void StopHaptic(void const *n) {
    haptic = 0;
    hapticTimer.stop();
}

void txTask(void) {
      
      while(1) {
          
        status = !kw40z_device.GetAdvertisementMode(); /*Indicate BLE Advertisment Mode*/   
        blueLed = status;
          
          if (tx_flag == 1) {
              
              checktime = stopwatch.read_ms();
              accel.acquire_accel_data_g(accel_data);
              mag.acquire_mag_data_uT(mag_data);
              gyro.acquire_gyro_data_dps(gyro_data);
              
              // counter += 1;
              //RPi.printf("[%4.5f] %4.3f %4.3f %4.3f %4.3f %4.3f %4.3f %4.3f %4.3f %4.3f \r\n", checktime, accel_data[0],accel_data[1],accel_data[2],mag_data[0],mag_data[1],mag_data[2],gyro_data[0],gyro_data[1],gyro_data[2]);
          
              for (int i = 0; i < 2; i++) {
                  RPi.putc('a');
              }
          
              for (int i = 0; i < 3 * sizeof(float); i++) {
                  RPi.putc(((uint8_t *) accel_data)[i]);
              }
          
              for (int i = 0; i < 2; i++) {
                  RPi.putc('g');
              }
          
              for (int i = 0; i < 3 * sizeof(float); i++) {
                  RPi.putc(((uint8_t *) gyro_data)[i]);
              }
          
              checktime = stopwatch.read_ms() - checktime;
          
              // RPi.printf("\r\n%4.5f \r\n", checktime);
          
              Thread::wait(10);
          }
          
          else {
              
              Thread::wait(1000);
          }
    }
    
    
}

void displayTask(void)  {
    
    /* Turn on the backlight of the OLED Display */
    oled.DimScreenON();
    
    /* Fills the screen with solid black */         
    oled.FillScreen(COLOR_BLACK);

    /* Get OLED Class Default Text Properties */
    oled_text_properties_t textProperties = {0};
    textProperties.alignParam = OLED_TEXT_ALIGN_CENTER;
    oled.GetTextProperties(&textProperties);
    
    /* Change font color to Blue */ 
    textProperties.fontColor   = COLOR_BLUE;
    oled.SetTextProperties(&textProperties);
    
    /* Display Bluetooth Label at x=17,y=65 */ 
    strcpy((char *) text,"MarkUp");
    oled.TextBox((uint8_t *)text,2,5, 91, 15); 
    
    /* Change font color to white */ 
    textProperties.fontColor   = COLOR_WHITE;
    textProperties.alignParam = OLED_TEXT_ALIGN_CENTER;
    oled.SetTextProperties(&textProperties);
    
    /* Display Label at x=22,y=80 */ 
    // oled_status_t SSD1351::TextBox(const uint8_t* text, int8_t xCrd, int8_t yCrd,uint8_t width,uint8_t height)
    strcpy((char *) text,"Tap Below");
    oled.TextBox((uint8_t *)text,2,40, 91, 15);
    strcpy((char *) text,"To Begin!");
    oled.TextBox((uint8_t *)text,2,55, 91, 15);
    
    int tx_change = tx_flag;
    
    
    while(1) {
        
        if (tx_change != tx_flag) {
            
            if (tx_flag == 0) {
                
                int r = rand() % 3 + 1;
                
                pc.printf("r = %d\r\n",r);

                if (r == 1) {
                    pc.printf("Ran r = %d\r\n",r);
                    strcpy((char *) text,"");
                    oled.TextBox((uint8_t *)text,2,25, 91, 15);
                    oled.TextBox((uint8_t *)text,2,40, 91, 15);
                    oled.TextBox((uint8_t *)text,2,55, 91, 15);
                    strcpy((char *) text,"Workout Done.");
                    oled.TextBox((uint8_t *)text,2,40, 91, 15);
                    strcpy((char *) text,"Ready for more?");
                    oled.TextBox((uint8_t *)text,2,55, 91, 15);
                    tx_change = tx_flag;
                }
                else if (r == 2) {
                    pc.printf("Ran r = %d\r\n",r);
                    strcpy((char *) text," ");
                    oled.TextBox((uint8_t *)text,2,25, 91, 15);
                    oled.TextBox((uint8_t *)text,2,40, 91, 15);
                    oled.TextBox((uint8_t *)text,2,55, 91, 15);
                    strcpy((char *) text,"Good stuff!");
                    oled.TextBox((uint8_t *)text,2,40, 91, 15);
                    strcpy((char *) text,"Do it again?");
                    oled.TextBox((uint8_t *)text,3,55, 91, 15);
                    tx_change = tx_flag;
                }
                else if (r == 3) {
                    pc.printf("Ran r = %d\r\n",r);
                    strcpy((char *) text,"");
                    oled.TextBox((uint8_t *)text,2,25, 91, 15);
                    oled.TextBox((uint8_t *)text,2,40, 91, 15);
                    oled.TextBox((uint8_t *)text,2,55, 91, 15);
                    strcpy((char *) text,"*final whistle*");
                    oled.TextBox((uint8_t *)text,2,40, 91, 15);
                    strcpy((char *) text,"Start again?");
                    oled.TextBox((uint8_t *)text,2,55, 91, 15);
                    tx_change = tx_flag;
                }

            }
            else {
                /* Display Label at x=22,y=80 */ 
                strcpy((char *) text,"Collecting...");
                oled.TextBox((uint8_t *)text,2,25, 91, 15);
                strcpy((char *) text,"Tap Below");
                oled.TextBox((uint8_t *)text,2,40, 91, 15);
                strcpy((char *) text,"To End.");
                oled.TextBox((uint8_t *)text,2,55, 91, 15);
                tx_change = tx_flag;
            }
        }
        else {
            
            Thread::wait(1000);   
        }
    }
}
