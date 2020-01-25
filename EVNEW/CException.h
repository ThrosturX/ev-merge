// EVNEW - Escape Velocity: Nova Editor for Windows
// By Adam Rosenfield
// (c) 2003 All Rights Reserved

// File CException.h

#ifndef CEXCEPTION_H_INCLUDED		// Prevent multiple inclusions
#define CEXCEPTION_H_INCLUDED

////////////////////////////////////////////////////////////////
///////////////////////  CLASS FORWARDS  ///////////////////////
////////////////////////////////////////////////////////////////

class CException;

////////////////////////////////////////////////////////////////
//////////////////////////  INCLUDES  //////////////////////////
////////////////////////////////////////////////////////////////

#include <string>

////////////////////////////////////////////////////////////////
///////////////////////////  CLASSES  //////////////////////////
////////////////////////////////////////////////////////////////

class CException
{
public:
	CException(void);							// Default constructor
	CException(char *szException, ...);			// Constructor with a printf-style string
	CException(const CException &exception);	// Copy constructor

	~CException(void);							// Destructor

	std::string GetExceptionString(void);		// Get the exception string (if there is one)

private:
	std::string m_szException;					// The exception string
};

#endif		// #ifndef CEXCEPTION_H_INCLUDED