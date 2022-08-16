#include <Wire.h>

float power,x,y;
int i=0,temp=0;
char a[5];

int decimalPrecision = 2;
int VoltageAnalogInputPin = A1;            
float voltageSampleRead  = 0;              
float voltageLastSample  = 0;               
float voltageSampleSum   = 0;              
float voltageSampleCount = 0;              
float voltageMean ;                          
float RMSVoltageMean ;                      
float adjustRMSVoltageMean;
float FinalRMSVoltage;                   
float voltageOffset1 =0.00 ;
float voltageOffset2 = 0.00;

#define SAMPLES 300
#define ACS_Pin A0 
float High_peak,Low_peak;    
float Amps_Peak_Peak, Amps_RMS;  

float voltage()
{
    while(voltageSampleCount<1000){
    if(micros()>=voltageLastSample+1000) 
    {     
      voltageSampleRead=(analogRead(VoltageAnalogInputPin)-512)+voltageOffset1;          
      voltageSampleSum=voltageSampleSum+sq(voltageSampleRead);                          
      voltageSampleCount=voltageSampleCount + 1;                                                        
      voltageLastSample=micros();  
    }                                                                       
    }
    if(voltageSampleCount==1000)                       
    {
        voltageMean=voltageSampleSum/voltageSampleCount;        
        RMSVoltageMean=(sqrt(voltageMean))*1.5;                                                                  
        adjustRMSVoltageMean=RMSVoltageMean+voltageOffset2;                                                                                                              
        FinalRMSVoltage=RMSVoltageMean+voltageOffset2;                                                       
        
        if(FinalRMSVoltage<=100)                                                                               
        {  
          FinalRMSVoltage=0;
        }
        if(FinalRMSVoltage>=270)                                                                               
        {  
          FinalRMSVoltage=0;
        }
      
        Serial.print("Voltage : ");
        Serial.print(FinalRMSVoltage,decimalPrecision);
        Serial.print("V");
        voltageSampleSum=0;                                                                                     
        voltageSampleCount=0;                                                                                     
     }
     
  return(FinalRMSVoltage,decimalPrecision);
}

float current()
{
  int cnt;           
  High_peak = 0;      
  Low_peak = 1024;
  
      for(cnt=0 ; cnt<SAMPLES ; cnt++)          
      {
        float ACS_Value = analogRead(ACS_Pin); 
        if(ACS_Value > High_peak)                
            {
              High_peak = ACS_Value;            
            }
        
        if(ACS_Value < Low_peak)                
            {
              Low_peak = ACS_Value;          
            }
       }              
      
      Amps_Peak_Peak = High_peak - Low_peak; 
      Amps_RMS = Amps_Peak_Peak*0.353*0.0165;
        
      Serial.print("  Amps: "); 
      Serial.print(Amps_RMS);
      Serial.println("A");      

  return Amps_RMS;
  
}

void requestEvent()
{
  temp=power*100;
  for(int i=0;i<5;i++)
  {
    a[i]=temp%10;
    temp=temp/10;
  }
  for(int i=0;i<5;i++)
    Wire.write(a[i]);
}

void setup()
{
  Serial.begin(9600);
  Wire.begin(9);
  Wire.onRequest(requestEvent);
  
  pinMode(ACS_Pin,INPUT);
  
  pinMode(5,OUTPUT);
  pinMode(6,OUTPUT);
  digitalWrite(5,HIGH);
  digitalWrite(6,HIGH);
  delay(500);

}

void loop()
{ 
  x=voltage();
  y=current();
  power = x*y*100;
  Serial.println(power);
  delay(500);  
}
