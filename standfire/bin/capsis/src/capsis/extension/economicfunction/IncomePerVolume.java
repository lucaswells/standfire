/*
 * Capsis 4 - Computer-Aided Projections of Strategies in Silviculture
 *
 * Copyright (C) 2000-2001  Francois de Coligny
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

package capsis.extension.economicfunction;

import java.util.Collection;

import jeeb.lib.util.Log;
import jeeb.lib.util.Translator;
import capsis.defaulttype.TreeList;
import capsis.extensiontype.EconomicFunction;
import capsis.kernel.GModel;
import capsis.kernel.GScene;
import capsis.kernel.MethodProvider;
import capsis.kernel.Step;
import capsis.kernel.extensiontype.GenericExtensionStarter;
import capsis.lib.economics.CommonEconFunctions;
import capsis.lib.economics.EconModel;
import capsis.lib.economics.EconStand;
import capsis.util.CancelException;
import capsis.util.methodprovider.VProvider;

/**
 * Calculate volume of removed wood during an intervention using getV function before and after intervention
 * A price is given to the wood removed : value
 *
 * @author C. Orazio - january 2003
 */
public class IncomePerVolume extends Income {

	protected double value;

	static {
		Translator.addBundle("capsis.extension.economicfunction.IncomePerVolume");
	}

	/**
	 * Phantom constructor.
	 * Only to ask for extension properties (authorName, version...).
	 */
	public IncomePerVolume () {}

	/**
	 * Official constructor. Uses an ExtensionStarter.
	 */
	public IncomePerVolume (GenericExtensionStarter s) throws Exception {
		try {
			stand = s.getScene ();	// stand is defined in EconomicFunction
			model = s.getModel ();	// model is defined in EconomicFunction

			// 1. Start mode according to context : interactive or not
			if (s instanceof IncomePerVolumeStarter) {

				// 2. Script mode starter
				IncomePerVolumeStarter p = (IncomePerVolumeStarter) s;
				value = p.value;

			} else {

				// 3. Interactive start
				IncomePerVolumeDialog dlg = new IncomePerVolumeDialog ();

				if (dlg.isValidDialog ()) {
					// valid -> ok was hit and check were ok
					value = dlg.getValue ();
				} else {
					throw new CancelException ();
				}
				dlg.dispose ();

			}

		} catch (Exception exc) {
			if (! (exc instanceof CancelException)) {	// do not log if cancel
				Log.println (Log.ERROR, "IncomePerVolume.c ()", exc.toString (), exc);
			}
			throw exc;
		}

	}

	/**
	 * String constructor. Uses an ExtensionStarter+ string
	 */
	public IncomePerVolume (GenericExtensionStarter s, String stringParameters) throws Exception {
		try {
			stand = s.getScene ();	// stand is defined in EconomicFunction
			model = s.getModel ();	// model is defined in EconomicFunction
			value = new Double (CommonEconFunctions.getValueFromString(stringParameters, 1, EconomicFunction.separator)).doubleValue();

		} catch (Exception exc) {
			if (! (exc instanceof CancelException)) {	// do not log if cancel
				Log.println (Log.ERROR,"String constructor "+"ExpenseConstant.c ()", exc.toString (), exc);
			}
			throw exc;
		}

	}

	/**
	 * Extension dynamic compatibility mechanism.
	 * This matchwith method checks if the extension can deal (i.e. is compatible) with the referent.
	 */
	public boolean matchWith (Object referent) {
		if (! (referent instanceof GModel)) {return false;}
		if (! (referent instanceof EconModel)) {return false;}

		GModel m = (GModel) referent;
		Step root = (Step) m.getProject ().getRoot ();
		GScene s = root.getScene ();
		if (! (s instanceof EconStand)) {return false;}

		MethodProvider mp = m.getMethodProvider ();
		if (mp == null) {return false;}
		if (! (mp instanceof VProvider)) {return false;}

		return true;
	}

	/**
	 * From EconomicFunction.
	 * Computation of the expense using getV function of model
	 * @return
	 */
	public double getResult () {
		String econTreesStatus = "cut";
		Collection trees = null;
		try {trees = ((TreeList) stand).getTrees (econTreesStatus);} catch (Exception e) {}
		return  value * ((VProvider) model.getMethodProvider ()).getV (stand, trees);
		
		/*Step stepfather = (Step) stand.getStep().getFather();
		GStand standfather = stepfather.getStand();

		fc - 8.4.2004
		Collection treesFather = null;
		
		try {treesFather = ((TreeCollection) standfather).getTrees ();} catch (Exception e) {}
		try {trees = ((TreeCollection) stand).getTrees ();} catch (Exception e) {}


		double v1 = 0;
		if (standfather != null){
			v1 = (double) ((VProvider) model.getMethodProvider ()).getV (standfather, treesFather);
		} else {
			v1 = 0;
		}
		double v2 = ((VProvider) model.getMethodProvider ()).getV (stand, trees);
		System.out.println (v1 + " v2:"+v2);
		return  (v1 - v2) * value;
		
		return  ((EconModel) model.getEconTool ("treeVolumeUsedForEconVolume")) (stand, trees);*/
	}

	/**
	 * From EconomicFunction.
	 */
	public String getFunctionParameters () {
		return getName ()
				+", "+Translator.swap ("IncomePerVolumeDialog.value")+"="+value
				;
	}
	/**
	* From EconomicFunction.
	*/
	public String getParametersList (){
		return Translator.swap ("IncomePerVolumeDialog.value")+separator;
	}

	/**
	 * From Extension interface.
	 */
	public String getName () {
		return Translator.swap ("IncomePerVolume");
	}

	/**
	 * From Extension interface.
	 */
	public String getVersion () {return VERSION;}
	public static final String VERSION = "1.1";

	/**
	 * From Extension interface.
	 */
	public String getAuthor () {return "C. Orazio";}

	/**
	 * From Extension interface.
	 */
	public String getDescription () {return Translator.swap ("IncomePerVolume.description");}

}
