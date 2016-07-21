/** 
 * Capsis - Computer-Aided Projections of Strategies in Silviculture
 * 
 * Copyright (C) 1999-2010 INRA 
 * 
 * Authors: F. de Coligny, S. Dufour-Kowalski, 
 * 
 * This file is part of Capsis
 * Capsis is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 2.1 of the License, or
 * (at your option) any later version.
 *
 * Capsis is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU lesser General Public License
 * along with Capsis.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

package capsis.util;

import java.awt.Dimension;

import javax.swing.Box;
import javax.swing.BoxLayout;

/**
 * RigidBox is a Box with preferred, maximum and minimum size equal.
 * 
 * @author F. de Coligny - january 2000
 */
public class RigidBox extends Box {

	public RigidBox (int axis) {
		super (axis);
	}

	public static Box createVerticalBox () {
		return new RigidBox (BoxLayout.Y_AXIS);
	}

	public static Box createHorizontalBox () {
		return new RigidBox (BoxLayout.X_AXIS);
	}

/*	public Dimension getPreferredSize () {
		return getMinimumSize ();
	}*/
	public Dimension getMaximumSize () {
		return getMinimumSize ();
	}
}