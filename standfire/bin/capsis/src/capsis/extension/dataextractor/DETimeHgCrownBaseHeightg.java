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

package capsis.extension.dataextractor;

import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.Vector;

import jeeb.lib.util.Log;
import jeeb.lib.util.Translator;
import capsis.extension.PaleoDataExtractor;
import capsis.kernel.GModel;
import capsis.kernel.GScene;
import capsis.kernel.MethodProvider;
import capsis.kernel.Step;
import capsis.kernel.extensiontype.GenericExtensionStarter;
import capsis.util.methodprovider.CrownBaseHeightgProvider;
import capsis.util.methodprovider.HgProvider;

/**
 * Quadratic mean Height and Quadratic mean Crown Base Height in terms of Time.
 *
 * @author C. Meredieu - T. Labbé september 2003
 */
public class DETimeHgCrownBaseHeightg extends DETimeG {
	protected Vector curves;
	protected Vector labels;

	static {
		Translator.addBundle("capsis.extension.dataextractor.DETimeHgCrownBaseHeightg");
	}

	/**
	 * Phantom constructor.
	 * Only to ask for extension properties (authorName, version...).
	 */
	public DETimeHgCrownBaseHeightg () {}

	/**
	 * Official constructor. It uses the standard Extension starter.
	 */
	public DETimeHgCrownBaseHeightg (GenericExtensionStarter s) {
		//~ this (s.getStep ());
	//~ }


	//~ /**
	 //~ * Functional constructor.
	 //~ */
	//~ protected DETimeHgCrownBaseHeightg (Step stp) {
		super (s);
		try {
			curves = new Vector ();
			labels = new Vector ();

			// This is Configuration stuff, not memorized in settings
			// Reminder: only MultiConfiguration stuff is memorized in settings.

		} catch (Exception e) {
			Log.println (Log.ERROR, "DETimeHgCrownBaseHeightg.c ()", "Exception occured while object construction : ", e);
		}
	}


	/**
	 * Extension dynamic compatibility mechanism.
	 * This matchwith method checks if the extension can deal (i.e. is compatible) with the referent.
	 */
	public boolean matchWith (Object referent) {
		try {
			if (!(referent instanceof GModel)) {return false;}
			GModel m = (GModel) referent;
			MethodProvider mp = m.getMethodProvider ();
			if (!(mp instanceof HgProvider)) {return false;}
			if (!(mp instanceof CrownBaseHeightgProvider)) {return false;}

		} catch (Exception e) {
			Log.println (Log.ERROR, "DETimeHgCrownBaseHeightg.matchWith ()", "Error in matchWith () (returned false)", e);
			return false;
		}

		return true;
	}


	/**
	 * This method is called by superclass DataExtractor.
	 */
	public void setConfigProperties () {
		// Choose configuration properties
		addConfigProperty (PaleoDataExtractor.TREE_GROUP);
		addConfigProperty (PaleoDataExtractor.I_TREE_GROUP);		// group individual configuration
	}


	/**
	 * From DataExtractor SuperClass.
	 *
	 * Computes the data series. This is the real output building.
	 * It needs a particular Step.
	 *
	 * Return false if trouble while extracting.
	 */
	public boolean doExtraction () {
		if (upToDate) {return true;}
		if (step == null) {return false;}

		// Retrieve method provider
		methodProvider = step.getProject ().getModel ().getMethodProvider ();

		try {
			// Retrieve Steps from root to this step
			Vector steps = step.getProject ().getStepsFromRoot (step);

			Vector c1 = new Vector ();		// x coordinates
			Vector c2 = new Vector ();		// y coordinates
			Vector c3 = new Vector ();		// y coordinates

			// Data extraction : points with (Integer, Double) coordinates
			for (Iterator i = steps.iterator (); i.hasNext ();) {
				Step s = (Step) i.next ();

				// Consider restriction to one particular group if needed
				GScene stand = s.getScene ();
				Collection trees = doFilter (stand);

				int date = stand.getDate ();

				// Rounded under
				double Hg = ((HgProvider) methodProvider).getHg (stand, trees);
				double CrownBaseHeightg = ((CrownBaseHeightgProvider) methodProvider).
						getCrownBaseHeightg (stand, trees);

				c1.add (new Integer (date));
				c2.add (new Double (Hg));
				c3.add (new Double (CrownBaseHeightg));
			}

			curves.clear ();
			curves.add (c1);
			curves.add (c2);
			curves.add (c3);

			labels.clear ();
			labels.add (new Vector ());		// no x labels
			Vector y1Labels = new Vector ();
			y1Labels.add ("Hg");
			labels.add (y1Labels);			// y1 : label "Hg"
			Vector y2Labels = new Vector ();
			y2Labels.add ("CBHg");
			labels.add (y2Labels);			// y2 : label "CBHg"

		} catch (Exception exc) {
			Log.println (Log.ERROR, "DETimeHgCrownBaseHeightg.doExtraction ()", "Exception caught : ",exc);
			return false;
		}

		upToDate = true;
		return true;
	}


	/**
	 * From DataFormat interface.
	 */
	public String getName() {
		return getNamePrefix ()+Translator.swap ("DETimeHgCrownBaseHeightg");
	}


	/**
	 * From DFCurves interface.
	 */
	public List<List<? extends Number>> getCurves () {
		return curves;
	}


	/**
	 * From DFCurves interface.
	 */
	public List<List<String>> getLabels () {
		return labels;
	}


	/**
	 * From DFCurves interface.
	 */
	public List<String> getAxesNames () {
		Vector v = new Vector ();
		v.add (Translator.swap ("DETimeHgCrownBaseHeightg.xLabel"));
		v.add (Translator.swap ("DETimeHgCrownBaseHeightg.yLabel"));
		return v;
	}


	/**
	 * From DFCurves interface.
	 */
	public int getNY () {
		return curves.size () - 1;
	}


	/**
	 * From Extension interface.
	 */
	public String getVersion () {return VERSION;}

	public static final String VERSION = "1.1";


	/**
	 * From Extension interface.
	 */
	public String getAuthor () {return "C. Meredieu - T. Labbé";}


	/**
	 * From Extension interface.
	 */
	public String getDescription () {return Translator.swap ("DETimeHgCrownBaseHeightg.description");}


}
