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

package capsis.extension.filter.general;

import java.io.Serializable;
import java.util.Collection;
import java.util.HashSet;
import java.util.Iterator;

import jeeb.lib.util.Identifiable;
import jeeb.lib.util.Log;
import jeeb.lib.util.Translator;
import capsis.commongui.util.Tools;
import capsis.extensiontype.Filter;
import capsis.util.Configurable;
import capsis.util.ConfigurationPanel;

/**
 * Filter for object containing Identifiable objects. (ex: GStand (resp. GPlot)
 * contain GTree (resp. GCell)). FIndividualSelector allows to choose elements
 * according to their id. Identifiable objects have a "int getId ()" method.
 * 
 * @author F. de Coligny - november 2000 / april 2004
 */
public class FIndividualSelector implements Filter, Configurable, Serializable {

	public static final String NAME = "FIndividualSelector";
	public static final String VERSION = "1.2";
	public static final String AUTHOR = "F. de Coligny";
	public static final String DESCRIPTION = "FIndividualSelector.description";

	// Filter can be configured by a config panel using its protected variables
	// wo accessors
	// fc - 21.5.2003 - added transient : filtrable is not used in retain () and
	// must not be serialized (huge)
	//
	transient protected Object referent; // complete original object (a complete
											// GStand or GPlot...)
	transient protected Collection candidates; // individuals to filter

	protected Collection toIds; // list of selected ids (current selection)
	private boolean readyToUse;

	static {
		Translator
				.addBundle("capsis.extension.filter.general.FIndividualSelector");
	}

	public FIndividualSelector() {
		toIds = new HashSet(); // must be specified with gui components (HashSet
								// is better than Vector for contains)
	}

	/**
	 * Constructor for non GUI mode. No more configuration required before
	 * preset () and retain ().
	 */
	public FIndividualSelector(Collection<Integer> c) {
		toIds = c;
		readyToUse = true; // it will work
	}
	
	public Object clone () {
		try {
			// We just need another instance to prevent preset () ant retain () from
			// being called by several threads at the same time. 
			return super.clone ();
		} catch (Exception e) {
			Log.println (Log.ERROR, "FIndividualSelector.clone ()", "Could not clone", e);
			return null;
		}
	}

	/**
	 * Used by extensionManager to look for compatibilities.
	 */
	static public boolean matchWith(Object o) {
		if (o instanceof Collection) {
			Collection c = (Collection) o;
			if (c.isEmpty()) {
				return false;
			}
			Collection reps = Tools.getRepresentatives(c); // one instance of
															// each class
			//
			// Possibly several subclasses of Identifiable
			for (Iterator i = reps.iterator(); i.hasNext();) {
				if (!(i.next() instanceof Identifiable)) {
					return false;
				}
			}
			return true;
		}
		return false;
	}

	/**
	 * Return true if the filter keeps the given individual. This means that the
	 * object corresponds to the rules of the filter.
	 */
	@Override
	public boolean retain(Object individual) throws Exception {
		// Check if can be applied
		if (!readyToUse) {
			throw new Exception(
					"FIndividualSelector.retain () - bad configuration for "
							+ toString());
		}

		Identifiable i = (Identifiable) individual;
		if (toIds.contains(new Integer(i.getId()))) {
			return true;
		}

		return false;
	}

	/**
	 * GUI use : configuration panel configures the filter before preset () and
	 * retain () are called.
	 */
	public ConfigurationPanel getConfigurationPanel(Object param) {
		// fc - 20.4.2004
		Object[] refAndCandidates = (Object[]) param;
		referent = refAndCandidates[0];
		candidates = (Collection) refAndCandidates[1];

		return new FIndividualSelectorConfigPanel(this);
	}

	/**
	 * GUI use : configuration panel configures the filter before preset () and
	 * retain () are called.
	 */
	public void configure(ConfigurationPanel panel) {
		FIndividualSelectorConfigPanel p = (FIndividualSelectorConfigPanel) panel;
		this.toIds = p.getToIds();

		readyToUse = true; // it will work
	}

	/** From Configurable interface. */
	public String getConfigurationLabel() {
		return Translator.swap(NAME);
	}

	// Needed because of Configurable and Extension interfaces, but unused
	@Override
	public void postConfiguration() {
	}

	@Override
	public void activate() {
	}

	@Override
	public void preset(Collection individuals) throws Exception {
		// TODO Auto-generated method stub

	}

}
