/* 
 * Spatial library for Capsis4.
 * 
 * Copyright (C) 2001-2003 Francois Goreaud.
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

package capsis.lib.spatial;

import capsis.kernel.AbstractSettings;

/**
 * Virtual3StrataParameters - List of parameters.
 * May have defaults or not. May be modified by user action during 
 * initialization process in interactive mode.
 *
 * @author F. Goreaud - june 2004 -> 17/6/04
 */
public class Virtual3StrataParameters extends AbstractSettings {

	// Default values
	// So ? - allows "reset" in dialogs - fc ;-)

	// Here we add all the parameters used to simulate virtual stands.

	public boolean virtualStand = true;
	public int virtualStandD = 4;
	public String virtualStandnDHFile = "test.nDH";
	public String virtualStandnDFile = "test.nD";
	public String virtualStandDHistFile = "test.hist";
	public int virtualStandTreeNumber = 109;
	public double virtualStandDMean = 36;
	public double virtualStandDDeviation = 7;
	public int virtualStandH = 2;
	public double virtualStandHMean = 29.5;
	public double virtualStandHDeviation = 1.7;
	public double virtualStandHCurve = 3;
	public double virtualStandH1a = 25.3;
	public double virtualStandH1b = 0.125;
	public double virtualStandH1c = 0;
	public double virtualStandH1d = 1;
	public double virtualStandH2a = 1.3;
	public double virtualStandH2K = 30;
	public double virtualStandH2b = 0.1;
	public double virtualStandH2d = 1;
	public double virtualStandH3a = 1.3;
	public double virtualStandH3b = 1.455;
	public double virtualStandH3c = 0.15; //0.1765;
	public double virtualStandH3d = 1;

	public int virtualStandXY = 1;
	public double virtualStandPrecision = 0.01;
	public double virtualStandXmin = 0;
	public double virtualStandXmax = 50;
	public double virtualStandYmin = 0;
	public double virtualStandYmax = 50;
	public int virtualStandClusterNumber = 10;
	public double virtualStandClusterRadius = 5;
	public double virtualStandGibbsR1 = 2;
	public double virtualStandGibbsCost1 = 100;
	public double virtualStandGibbsR2 = 5;
	public double virtualStandGibbsCost2 = -1;
	public double virtualStandGibbsR3 = 0;
	public double virtualStandGibbsCost3 = 0;
	public int virtualStandGibbsIteration = 600;
	public int virtualStandGibbsInterval = 2;

}


