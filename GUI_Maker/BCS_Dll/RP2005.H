//---------------------------------------------------------------------------
// Built with Microsoft Visual C++ 5.0 SP3
// Version 2.01
/*
Error Codes
0x0000	OK
0x0001	Invalid Handle
0x0002	Device Not Found
0x0003	Device Not Opened
0x0004	IO Error
0x0005	Insufficient Resources
0x0006	Invalid Parameter
0x0010	Other Error
0x0020	Not a valid Input port
0x0040	Incorrect input port value sent, possible USB transfer error
0x0080	Not a valid Output port
0x0100	Unknown error	
0x0200	Unknown command byte	
0x0400	Unknown error	
0x0800	Unknown request byte returned, possible USB transfer error	
0x1000	Incorrect command returned	
0x2000	Time out reading from the device	
0x4000	Incorrect number of bytes written to device	
0x8000		
*/

__declspec(dllexport) unsigned long __stdcall RP_ListDIO(int *NumBrds, char *SN, char *Dsc);
__declspec(dllexport) unsigned long __stdcall RP_OpenDIO(char *SN, unsigned long *hDIO);
__declspec(dllexport) unsigned long __stdcall RP_CloseDIO(unsigned long hDIO);
__declspec(dllexport) unsigned long __stdcall RP_GetVer(unsigned long hDIO, char *SWVer, char *ErrMsg);
__declspec(dllexport) unsigned long __stdcall RP_ReadPort(unsigned long hDIO, unsigned char ucPort, unsigned char *PVal, char *ErrMsg);
__declspec(dllexport) unsigned long __stdcall RP_ReadAll(unsigned long hDIO, unsigned long *ulLP, unsigned long *ulHP, char *ErrMsg);
__declspec(dllexport) unsigned long __stdcall RP_WriteAll(unsigned long hDIO, unsigned long ulLP, unsigned long ulHP, char *ErrMsg);
__declspec(dllexport) unsigned long __stdcall RP_WritePort(unsigned long hDIO, unsigned char ucPort, unsigned char PVal, char *ErrMsg);
// Added the following functions. They will open the device, perform the function and then close the device.
__declspec(dllexport) unsigned long __stdcall RP_GetVer_SN(char *SN, char *SWVer, char *ErrMsg);
__declspec(dllexport) unsigned long __stdcall RP_ReadPort_SN(char *SN, unsigned char ucPort, unsigned char *PVal, char *ErrMsg);
__declspec(dllexport) unsigned long __stdcall RP_ReadAll_SN(char *SN, unsigned long *ulLP, unsigned long *ulHP, char *ErrMsg);
__declspec(dllexport) unsigned long __stdcall RP_WriteAll_SN(char *SN, unsigned long ulLP, unsigned long ulHP, char *ErrMsg);
__declspec(dllexport) unsigned long __stdcall RP_WritePort_SN(char *SN, unsigned char ucPort, unsigned char PVal, char *ErrMsg);

