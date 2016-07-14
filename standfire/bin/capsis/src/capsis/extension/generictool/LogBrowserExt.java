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
package capsis.extension.generictool;

import java.awt.Window;

import javax.swing.JFrame;

import jeeb.lib.util.LogBrowser;
import jeeb.lib.util.Translator;
import capsis.extensiontype.GenericTool;

/**
 * LogBrowserExt opens the LogBrowser to show the log files (*.log).
 * 
 * @author F. de Coligny - june 2001
 */
public class LogBrowserExt implements GenericTool {

	static {
		Translator.addBundle ("capsis.extension.generictool.LogBrowserExt");
	}
	public static final String NAME = Translator.swap ("LogBrowserExt");
	public static final String DESCRIPTION = Translator.swap ("LogBrowserExt.description");
	public static final String AUTHOR = "F. de Coligny";
	public static final String VERSION = "1.1";

	private LogBrowser browser;

	/**
	 * Default constructor.
	 */
	public LogBrowserExt () {
	}

	@Override
	public void init (Window window) throws Exception {

		browser = new LogBrowser (window);
		browser.selectLog ("capsis");
		browser.refreshContent ();

	}

	/**
	 * Extension compatibility system. Returns true if the extension can deal
	 * with the given object.
	 */
	static public boolean matchWith (Object referent) {
		return true;
	}

	@Override
	public void activate () {
	}

}