/* 
 * Capsis 4 - Computer-Aided Projections of Strategies in Silviculture
 * 
 * Copyright (C) 2000-2003  Francois de Coligny
 * 
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 * 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied 
 * warranty of MERCHANTABILITY or FITNESS FOR A 
 * PARTICULAR PURPOSE. See the GNU Lesser General Public 
 * License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

package capsis.extension.modeltool.amapsim2;

import java.io.IOException;

import capsis.util.SwapDataInputStream;

/**
 * IdRequestResponse.
 * 
 * @author F. de Coligny - january 2004
 */
public class IdRequestResponse extends Response {

	// Data to be received
	public int dataLength;		// this field is not counted in dataLength	
	public String messageId;	// 5 chars without NULL after
	public int requestType;		// 7
	public int returnCode;		// 0 = correct, other, see server nomenclature

	public String req7Id;	// 5 octets
	public int ipServer;	// 4 octets
	
	
	public IdRequestResponse (SwapDataInputStream in) throws IOException {
		super (in);
		
		if (in == null) {
			return;
		}
		
		dataLength = in.readInt ();
		StringBuffer sb = new StringBuffer ();
		for (int i = 0; i < 5; i++) {
			sb.append ((char) in.readByte ());
		}
		messageId = sb.toString ();
		requestType = in.readInt ();
		returnCode = in.readInt ();
		
		req7Id = Response.readString (in);	
		ipServer = in.readInt ();
		
	}
	
	public int getDataLength () {return dataLength;}
	public String getMessageId () {return messageId;}
	public int getRequestType () {return requestType;}
	public int getReturnCode () {return returnCode;}
	
	public String getReq7Id () {return req7Id;}
	public int getIpServer () {return ipServer;}
	
	
	
	public String toString () {
		return "IdRequestResponse: dataLength="+dataLength+" messageId="+messageId
				+" requestType="+requestType+" returnCode="+returnCode;
	}
}

