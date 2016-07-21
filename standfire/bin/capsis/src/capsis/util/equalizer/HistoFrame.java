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

package capsis.util.equalizer;

import javax.swing.JFrame;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

/**	Equalizer test.
* 
*	@author F. de Coligny - september 2002
*/
public class HistoFrame extends JFrame implements ChangeListener {

	
	public void stateChanged (ChangeEvent evt) {
		System.out.print ("Someone changed my equalizer, new values = ");
		Equalizer e = (Equalizer) evt.getSource ();
		for (int i = 0; i < e.getValues ().length; i++) {
			System.out.print (e.getValues ()[i]+" ");
		}
		System.out.println ();
	}
	
	
	public HistoFrame (String name) {
		super (name);
	}
	
	

}
