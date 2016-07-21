/* 
 * Capsis 4 - Computer-Aided Projections of Strategies in Silviculture
 * 
 * Copyright (C) 2000-2011  Francois de Coligny
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

package capsis.util.methodprovider;

import capsis.defaulttype.MultipartScene;
import capsis.defaulttype.ScenePart;

/**	An interface for stem number to be applied 
 * 	on the parts of a multipart scene (ScenePart, MultipartScene).
 * 
 *	@author F. de Coligny - january 2011 
 */

public interface MuN {
	
	/** Returns the stem number of the given ScenePart.	
	 */
	public int getN (MultipartScene scene, ScenePart part);

}
